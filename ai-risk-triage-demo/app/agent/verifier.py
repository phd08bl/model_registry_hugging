from __future__ import annotations

from typing import Any

from pydantic import ValidationError

from app.agent.tools import evidence_line_numbers, prompt_injection_indicators
from app.schemas import (
    EvidenceExtraction,
    ToolContract,
    ToolResult,
    VerificationResult,
    VerificationStatus,
)
from app.versions import RULESET_VERSION

PROHIBITED_OUTPUT_PATTERNS = (
    "bypass gate",
    "skip mandatory gate",
    "change materiality threshold",
    "change materiality score",
    "upgrade autonomy",
    "approve the case",
)


class ResultVerifier:
    """Deterministic checks around tool output; semantic limits remain explicit."""

    def verify(
        self,
        result: ToolResult,
        contract: ToolContract,
        state: dict[str, Any],
        minimum_confidence: float,
    ) -> VerificationResult:
        issues: list[str] = []
        limitations: list[str] = []
        try:
            if contract.output_schema == "EvidenceExtraction":
                EvidenceExtraction.model_validate(result.output)
            elif not isinstance(result.output, dict):
                raise TypeError("Tool output must be a structured object.")
            output_schema_valid = True
        except (ValidationError, TypeError, ValueError):
            output_schema_valid = False

        invocation = state.get("current_tool_invocation", {}) or {}
        checks = {
            "status": result.status == "succeeded",
            "output_schema_valid": output_schema_valid,
            "case_identity": result.case_id == state.get("case_id"),
            "tool_identity": result.tool_id == contract.tool_id,
            "tool_version": result.tool_version == contract.version,
            "invocation_identity": (
                not invocation or result.invocation_id == invocation.get("invocation_id")
            ),
            "case_state_version": (
                not invocation
                or (
                    result.case_state_version == invocation.get("case_state_version")
                    == state.get("case_state_version", 1)
                )
            ),
            "result_rule_version": (
                not invocation
                or result.rule_version == invocation.get("rule_version") == state.get("rule_version")
            ),
            "state_fingerprint": (
                not invocation
                or result.state_fingerprint == invocation.get("state_fingerprint")
            ),
            "rule_version_current": state.get("rule_version", RULESET_VERSION) == RULESET_VERSION,
            "confidence": result.confidence >= minimum_confidence,
            "no_unauthorised_external_action": not bool(
                result.output.get("external_write") is True
            ),
        }

        output_text = str(result.output).lower()
        checks["no_deterministic_rule_change"] = not any(
            term in output_text for term in PROHIBITED_OUTPUT_PATTERNS
        )

        valid_lines = evidence_line_numbers(str(state.get("evidence_text", "")))
        raw_facts = result.output.get("facts", [])
        facts = (
            [fact for fact in raw_facts if isinstance(fact, dict)]
            if isinstance(raw_facts, list)
            else []
        )
        cited_lines = [line for fact in facts for line in fact.get("line_refs", [])]
        checks["citations_exist"] = all(line in valid_lines for line in cited_lines)
        evidence_lines = str(state.get("evidence_text", "")).splitlines()
        citation_support = []
        for fact in facts:
            claim_terms = {
                token.strip(".,:;()[]").lower()
                for token in str(fact.get("claim", "")).split()
                if len(token.strip(".,:;()[]")) >= 4
            }
            cited_text = " ".join(
                evidence_lines[line - 1]
                for line in fact.get("line_refs", [])
                if line in valid_lines
            ).lower()
            citation_support.append(
                not claim_terms or any(term in cited_text for term in claim_terms)
            )
        checks["citations_support_claims"] = all(citation_support)
        if result.tool_id.value == "evidence_extractor" and facts:
            checks["claims_have_sources"] = all(bool(fact.get("line_refs")) for fact in facts)
        else:
            checks["claims_have_sources"] = True

        indicators = prompt_injection_indicators(str(state.get("evidence_text", "")))
        checks["untrusted_evidence_not_authority"] = checks["no_deterministic_rule_change"]
        output_conflicts = result.output.get("inconsistencies")
        checks["unresolved_conflicts_preserved"] = (
            contract.permission == "deterministic"
            or output_conflicts is None
            or set(state.get("inconsistencies", [])).issubset(set(output_conflicts))
        )
        if indicators:
            issues.append("Possible prompt-injection text was recorded as untrusted evidence.")

        for name, passed in checks.items():
            if not passed:
                issues.append(f"Verification check failed: {name}")

        semantic_tools = {
            "evidence_extractor",
            "rag_evidence_checker",
            "agentic_ai_autonomy_checker",
            "supplier_evidence_checker",
            "challenge_assessor",
        }
        if result.tool_id.value in semantic_tools:
            limitations.append("Full semantic correctness cannot be established deterministically.")

        hard_failure = not all(
            checks[name]
            for name in (
                "status",
                "output_schema_valid",
                "case_identity",
                "tool_identity",
                "tool_version",
                "invocation_identity",
                "case_state_version",
                "result_rule_version",
                "state_fingerprint",
                "rule_version_current",
                "no_unauthorised_external_action",
                "no_deterministic_rule_change",
                "citations_exist",
                "citations_support_claims",
                "claims_have_sources",
                "unresolved_conflicts_preserved",
            )
        )
        if hard_failure:
            disposition = "escalate"
        elif not checks["confidence"] or limitations or result.advisory:
            disposition = "advisory"
        else:
            disposition = "accepted"
        verified = not hard_failure and checks["confidence"]
        return VerificationResult(
            verified=verified,
            disposition=disposition,
            status=(VerificationStatus.EXECUTION_FAILED if result.status == "failed" else None),
            checks=checks,
            limitations=limitations,
            issues=issues,
            label=(
                "Advisory observation—AIRO confirmation required."
                if disposition == "advisory"
                else None
            ),
        )
