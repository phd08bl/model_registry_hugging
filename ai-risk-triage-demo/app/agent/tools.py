from __future__ import annotations

import re
from collections.abc import Callable
from time import perf_counter
from typing import Any

from pydantic import BaseModel, ValidationError

from app.engines.lod2 import calculate_2lod_triggers
from app.engines.materiality import calculate_materiality
from app.llm.base import LLMClient
from app.schemas import (
    AutonomyProfile,
    EvidenceExtraction,
    ToolContract,
    ToolIdentifier,
    ToolInvocation,
    ToolResult,
)
from app.services.evidence import (
    build_targeted_questions,
    deterministic_evidence_checks,
    numbered_text,
)
from app.services.review_pack import build_review_pack

ALL_PROFILES: set[AutonomyProfile] = {
    "human_governed",
    "conditional_review",
    "exception_based",
    "straight_through",
    "straight_through_demo",
}


class EvidenceToolInput(BaseModel):
    questionnaire: dict[str, Any]
    evidence_text: str


class StateToolInput(BaseModel):
    state: dict[str, Any]


class LocalDraftInput(BaseModel):
    case_id: str
    content: dict[str, Any]


def _contract(
    tool_id: ToolIdentifier,
    purpose: str,
    permission: str = "advisory",
    risk: str = "low",
    status: str = "implemented",
    input_schema: str = "StateToolInput",
    output_schema: str = "dict",
    approval: bool = False,
    idempotent: bool = True,
) -> ToolContract:
    return ToolContract(
        tool_id=tool_id,
        version="demo-1.0",
        purpose=purpose,
        input_schema=input_schema,
        output_schema=output_schema,
        permission=permission,
        risk_classification=risk,
        timeout_seconds=30,
        max_retries=1,
        idempotency_required=idempotent,
        human_approval_required=approval,
        allowed_profiles=ALL_PROFILES,
        implementation_status=status,
    )


class ToolRegistry:
    """Single allowlist and execution boundary for Coordinator tools."""

    def __init__(self, llm: LLMClient):
        self.llm = llm
        self._contracts = self._build_contracts()
        self._results_by_key: dict[str, ToolResult] = {}
        self._handlers: dict[ToolIdentifier, Callable[[dict[str, Any]], dict[str, Any]]] = {
            ToolIdentifier.DOCUMENT_PARSER: self._parse_document,
            ToolIdentifier.EVIDENCE_EXTRACTOR: self._extract_evidence,
            ToolIdentifier.POLICY_RETRIEVER: self._retrieve_demo_policy,
            ToolIdentifier.EVIDENCE_CONSISTENCY_CHECKER: self._check_consistency,
            ToolIdentifier.RAG_EVIDENCE_CHECKER: self._check_rag,
            ToolIdentifier.AGENTIC_AUTONOMY_CHECKER: self._check_agentic,
            ToolIdentifier.SUPPLIER_EVIDENCE_CHECKER: self._check_supplier,
            ToolIdentifier.FOLLOW_UP_QUESTION_GENERATOR: self._follow_up_questions,
            ToolIdentifier.CHALLENGE_ASSESSOR: self._challenge,
            ToolIdentifier.CITATION_VERIFIER: self._verify_citations,
            ToolIdentifier.MATERIALITY_ENGINE: self._materiality,
            ToolIdentifier.LOD2_TRIGGER_ENGINE: self._lod2,
            ToolIdentifier.REVIEW_PACK_GENERATOR: self._review_pack,
            ToolIdentifier.CONFLUENCE_DRAFT_CREATOR: self._local_confluence_demo,
            ToolIdentifier.EMAIL_TASK_ADAPTER: self._local_task_demo,
        }

    @staticmethod
    def _build_contracts() -> dict[ToolIdentifier, ToolContract]:
        values = [
            _contract(
                ToolIdentifier.DOCUMENT_PARSER,
                "Parse supplied text without external access",
                "read_only",
                input_schema="EvidenceToolInput",
            ),
            _contract(
                ToolIdentifier.EVIDENCE_EXTRACTOR,
                "Extract evidence claims with source references",
                input_schema="EvidenceToolInput",
                output_schema="EvidenceExtraction",
            ),
            _contract(
                ToolIdentifier.POLICY_RETRIEVER,
                "Retrieve versioned illustrative demo policy",
                "read_only",
            ),
            _contract(
                ToolIdentifier.EVIDENCE_CONSISTENCY_CHECKER,
                "Apply deterministic questionnaire/evidence consistency checks",
                "deterministic",
                input_schema="EvidenceToolInput",
            ),
            _contract(
                ToolIdentifier.RAG_EVIDENCE_CHECKER, "Identify RAG-specific evidence observations"
            ),
            _contract(
                ToolIdentifier.AGENTIC_AUTONOMY_CHECKER,
                "Identify autonomy-control evidence observations",
            ),
            _contract(
                ToolIdentifier.SUPPLIER_EVIDENCE_CHECKER, "Identify supplier evidence observations"
            ),
            _contract(
                ToolIdentifier.FOLLOW_UP_QUESTION_GENERATOR, "Generate advisory follow-up questions"
            ),
            _contract(
                ToolIdentifier.CHALLENGE_ASSESSOR, "Produce a bounded advisory challenge assessment"
            ),
            _contract(
                ToolIdentifier.CITATION_VERIFIER,
                "Verify submitted-evidence line references",
                "verification",
            ),
            _contract(
                ToolIdentifier.MATERIALITY_ENGINE,
                "Run the approved illustrative deterministic materiality rules",
                "deterministic",
            ),
            _contract(
                ToolIdentifier.LOD2_TRIGGER_ENGINE,
                "Run the approved illustrative deterministic 2LoD triggers",
                "deterministic",
            ),
            _contract(
                ToolIdentifier.REVIEW_PACK_GENERATOR,
                "Prepare a reversible local review pack",
                "read_only",
            ),
            _contract(
                ToolIdentifier.CONFLUENCE_DRAFT_CREATOR,
                "Safe local demonstration of a future Confluence draft adapter",
                "write",
                "high",
                "mocked",
                input_schema="LocalDraftInput",
                approval=True,
            ),
            _contract(
                ToolIdentifier.EMAIL_TASK_ADAPTER,
                "Safe local demonstration of a future email/task adapter",
                "write",
                "high",
                "mocked",
                input_schema="LocalDraftInput",
                approval=True,
            ),
        ]
        return {item.tool_id: item for item in values}

    def contracts(self) -> list[ToolContract]:
        return list(self._contracts.values())

    def get(self, tool_id: ToolIdentifier | str) -> ToolContract:
        try:
            key = ToolIdentifier(tool_id)
            return self._contracts[key]
        except (ValueError, KeyError) as exc:
            raise ValueError(f"Unknown tool '{tool_id}' fails closed.") from exc

    @staticmethod
    def _validate_inputs(contract: ToolContract, values: dict[str, Any]) -> None:
        model = {
            "EvidenceToolInput": EvidenceToolInput,
            "StateToolInput": StateToolInput,
            "LocalDraftInput": LocalDraftInput,
        }.get(contract.input_schema)
        if model:
            model.model_validate(values)

    @staticmethod
    def _validate_output(contract: ToolContract, values: dict[str, Any]) -> None:
        if not isinstance(values, dict):
            raise TypeError("Tool output must be a structured object.")
        if contract.output_schema == "EvidenceExtraction":
            EvidenceExtraction.model_validate(values)

    def invoke(
        self,
        invocation: ToolInvocation,
        effective_profile: AutonomyProfile,
        external_write_permitted: bool = False,
    ) -> ToolResult:
        contract = self.get(invocation.tool_id)
        if invocation.tool_version != contract.version:
            return self._failure(invocation, "Tool version is not the approved version.")
        if effective_profile not in contract.allowed_profiles:
            return self._failure(invocation, "Effective profile may not use this tool.")
        if contract.human_approval_required and not (
            invocation.approved_by and external_write_permitted
        ):
            return self._failure(
                invocation,
                "Explicit policy permission and AIRO approval are required.",
                "prohibited",
            )
        if contract.idempotency_required and invocation.idempotency_key in self._results_by_key:
            return self._results_by_key[invocation.idempotency_key].model_copy(
                update={
                    "invocation_id": invocation.invocation_id,
                    "idempotent_replay": True,
                }
            )
        if contract.implementation_status == "future_adapter":
            return self._failure(invocation, "Tool is a future adapter and cannot execute.")
        started = perf_counter()
        result: ToolResult | None = None
        for retry_count in range(contract.max_retries + 1):
            try:
                self._validate_inputs(contract, invocation.inputs)
                output = self._handlers[invocation.tool_id](invocation.inputs)
                self._validate_output(contract, output)
                duration_ms = (perf_counter() - started) * 1000
                if duration_ms > contract.timeout_seconds * 1000:
                    result = self._failure(
                        invocation,
                        "Tool exceeded its contract timeout.",
                        retry_count=retry_count,
                        duration_ms=duration_ms,
                        timed_out=True,
                    )
                else:
                    result = ToolResult(
                        invocation_id=invocation.invocation_id,
                        case_id=invocation.case_id,
                        tool_id=invocation.tool_id,
                        tool_version=contract.version,
                        status="succeeded",
                        output=output,
                        source_references=list(output.get("source_references", [])),
                        confidence=float(output.get("confidence", 1.0)),
                        advisory=contract.permission == "advisory",
                        retry_count=retry_count,
                        duration_ms=duration_ms,
                    )
                break
            except (ValidationError, KeyError, TypeError, ValueError, RuntimeError) as exc:
                result = self._failure(
                    invocation,
                    str(exc),
                    retry_count=retry_count,
                    duration_ms=(perf_counter() - started) * 1000,
                )
        assert result is not None
        if contract.idempotency_required:
            self._results_by_key[invocation.idempotency_key] = result
        return result

    @staticmethod
    def _failure(
        invocation: ToolInvocation,
        error: str,
        status: str = "failed",
        *,
        retry_count: int = 0,
        duration_ms: float = 0,
        timed_out: bool = False,
    ) -> ToolResult:
        return ToolResult(
            invocation_id=invocation.invocation_id,
            case_id=invocation.case_id,
            tool_id=invocation.tool_id,
            tool_version=invocation.tool_version,
            status=status,
            error=error,
            advisory=True,
            confidence=0,
            retry_count=retry_count,
            duration_ms=duration_ms,
            timed_out=timed_out,
        )

    @staticmethod
    def _parse_document(values: dict[str, Any]) -> dict[str, Any]:
        text = values["evidence_text"]
        return {"numbered_text": numbered_text(text), "line_count": len(text.splitlines())}

    def _extract_evidence(self, values: dict[str, Any]) -> dict[str, Any]:
        extraction = self.llm.extract_evidence(
            values["questionnaire"], numbered_text(values["evidence_text"])
        )
        refs = [
            f"submitted_evidence:line:{line}"
            for fact in extraction.facts
            for line in fact.line_refs
        ]
        confidence = min((fact.confidence for fact in extraction.facts), default=0.75)
        return {
            **extraction.model_dump(),
            "source_references": sorted(set(refs)),
            "confidence": confidence,
        }

    @staticmethod
    def _check_consistency(values: dict[str, Any]) -> dict[str, Any]:
        missing, inconsistencies = deterministic_evidence_checks(
            values["questionnaire"], values["evidence_text"]
        )
        return {
            "mandatory_evidence_gaps": missing,
            "inconsistencies": inconsistencies,
            "confidence": 1.0,
        }

    @staticmethod
    def _retrieve_demo_policy(values: dict[str, Any]) -> dict[str, Any]:
        return {
            "policy_version": "illustrative-demo-agent-policy-1.0",
            "notice": "Illustrative demo policy only; not approved PwC or MRO methodology.",
        }

    @staticmethod
    def _check_rag(values: dict[str, Any]) -> dict[str, Any]:
        text = str(values.get("state", {}).get("evidence_text", "")).lower()
        observations = []
        if not any(term in text for term in ("grounding", "retrieval", "access filtering")):
            observations.append("RAG grounding and retrieval-boundary controls are not evidenced.")
        if not any(term in text for term in ("citation", "source reference", "source identifier")):
            observations.append("RAG answer citations and source identifiers require confirmation.")
        return {"observations": observations, "confidence": 0.75}

    @staticmethod
    def _check_agentic(values: dict[str, Any]) -> dict[str, Any]:
        text = str(values.get("state", {}).get("evidence_text", "")).lower()
        observations = []
        checks = {
            "Action limits and permitted tools require confirmation.": (
                "action limit",
                "cannot access",
            ),
            "Human approval before consequential action requires confirmation.": (
                "human approval",
                "requires human",
            ),
            "Pause or stop controls require confirmation.": ("kill switch", "kill-switch", "pause"),
            "Reversibility and rollback controls require confirmation.": ("rollback", "reversible"),
        }
        for observation, terms in checks.items():
            if not any(term in text for term in terms):
                observations.append(observation)
        return {"observations": observations, "confidence": 0.75}

    @staticmethod
    def _check_supplier(values: dict[str, Any]) -> dict[str, Any]:
        text = str(values.get("state", {}).get("evidence_text", "")).lower()
        observations = []
        checks = {
            "Supplier contract evidence requires confirmation.": ("contract",),
            "Supplier due-diligence or assurance evidence requires confirmation.": (
                "due diligence",
                "assurance",
            ),
            "Supplier model-change responsibility requires confirmation.": (
                "model-change",
                "change responsibility",
            ),
        }
        for observation, terms in checks.items():
            if not any(term in text for term in terms):
                observations.append(observation)
        return {"observations": observations, "confidence": 0.75}

    @staticmethod
    def _follow_up_questions(values: dict[str, Any]) -> dict[str, Any]:
        state = values.get("state", {})
        return {
            "questions": build_targeted_questions(
                state.get("missing_information", []), state.get("inconsistencies", [])
            ),
            "confidence": 1.0,
        }

    def _challenge(self, values: dict[str, Any]) -> dict[str, Any]:
        challenge = self.llm.challenge(values["state"])
        return {**challenge.model_dump(), "confidence": 0.75}

    @staticmethod
    def _verify_citations(values: dict[str, Any]) -> dict[str, Any]:
        state = values.get("state", {})
        line_count = len(str(state.get("evidence_text", "")).splitlines())
        invalid = []
        for fact in state.get("evidence_extraction", {}).get("facts", []):
            invalid.extend(
                line for line in fact.get("line_refs", []) if line < 1 or line > line_count
            )
        return {"valid": not invalid, "invalid_line_refs": invalid, "confidence": 1.0}

    @staticmethod
    def _materiality(values: dict[str, Any]) -> dict[str, Any]:
        return calculate_materiality(values["state"]["questionnaire"])

    @staticmethod
    def _lod2(values: dict[str, Any]) -> dict[str, Any]:
        return calculate_2lod_triggers(values["state"]["questionnaire"])

    @staticmethod
    def _review_pack(values: dict[str, Any]) -> dict[str, Any]:
        return build_review_pack(values["state"])

    @staticmethod
    def _local_confluence_demo(values: dict[str, Any]) -> dict[str, Any]:
        return {
            "local_demo_reference": f"local-demo://confluence-draft/{values['case_id']}",
            "external_write": False,
        }

    @staticmethod
    def _local_task_demo(values: dict[str, Any]) -> dict[str, Any]:
        return {
            "local_demo_reference": f"local-demo://task/{values['case_id']}",
            "external_write": False,
        }


def evidence_line_numbers(text: str) -> set[int]:
    """Return valid line identifiers for deterministic citation verification."""

    return set(range(1, len(text.splitlines() or [""]) + 1))


def prompt_injection_indicators(text: str) -> list[str]:
    patterns = (
        r"ignore (?:(all|any|the) )?previous instructions",
        r"system prompt",
        r"bypass (the )?(gate|policy|approval)",
        r"change (the )?(rules|threshold|materiality)",
    )
    lowered = text.lower()
    return [pattern for pattern in patterns if re.search(pattern, lowered)]
