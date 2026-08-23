from __future__ import annotations

from typing import Any

from app.agent.tools import evidence_line_numbers, prompt_injection_indicators
from app.schemas import ToolContract, ToolResult, VerificationResult

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
        checks = {
            "status": result.status == "succeeded",
            "case_identity": result.case_id == state.get("case_id"),
            "tool_identity": result.tool_id == contract.tool_id,
            "tool_version": result.tool_version == contract.version,
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
        cited_lines = [
            line for fact in result.output.get("facts", []) for line in fact.get("line_refs", [])
        ]
        checks["citations_exist"] = all(line in valid_lines for line in cited_lines)
        if result.tool_id.value == "evidence_extractor" and result.output.get("facts"):
            checks["claims_have_sources"] = all(
                bool(fact.get("line_refs")) for fact in result.output["facts"]
            )
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
                "case_identity",
                "tool_identity",
                "tool_version",
                "no_unauthorised_external_action",
                "no_deterministic_rule_change",
                "citations_exist",
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
            checks=checks,
            limitations=limitations,
            issues=issues,
            label=(
                "Advisory observation—AIRO confirmation required."
                if disposition == "advisory"
                else None
            ),
        )
