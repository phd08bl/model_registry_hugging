from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from app.agent.policy import ACTION_INPUTS, ACTION_TO_TOOL
from app.schemas import ActionAuthorisation, ActionProposal, SupervisorDecision, ToolContract
from app.versions import RULESET_VERSION


class ActionAuthoriser:
    """Final deterministic permission check immediately before every routed tool call."""

    @staticmethod
    def _required_inputs_present(proposal: ActionProposal, state: dict[str, Any]) -> bool:
        required = ACTION_INPUTS.get(proposal.selected_action, [])
        return all(
            key == "state" or (key in state and state.get(key) is not None) for key in required
        )

    def authorise(
        self,
        proposal: ActionProposal,
        state: dict[str, Any],
        supervisor: SupervisorDecision,
        contract: ToolContract | None,
    ) -> ActionAuthorisation:
        expected_tool = ACTION_TO_TOOL.get(proposal.selected_action)
        checks = {
            "action_allowed": proposal.selected_action in supervisor.allowed_actions,
            "tool_registered": contract is not None,
            "tool_allowlisted": (
                proposal.selected_tool is None or proposal.selected_tool in supervisor.allowed_tools
            ),
            "tool_matches_action": proposal.selected_tool == expected_tool,
            "required_inputs_present": self._required_inputs_present(proposal, state),
            "data_permissions_satisfied": bool(
                contract is None
                or not contract.data_permissions
                or all(permission != "DENIED" for permission in contract.data_permissions)
            ),
            "policy_version_current": (
                state.get("policy_version", supervisor.policy_version) == supervisor.policy_version
            ),
            "rule_version_current": state.get("rule_version") == RULESET_VERSION,
            "tool_contract_version_current": bool(
                contract is None
                or state.get("tool_contract_version") == contract.version
            ),
            "tool_budget_available": (
                proposal.selected_tool is None or supervisor.remaining_tool_calls > 0
            ),
            "loop_budget_available": supervisor.remaining_total_loops > 0,
            "confidence_sufficient": proposal.confidence
            >= float(state.get("policy_assessment", {}).get("minimum_confidence", 0.70)),
            "human_authority_not_pending": not bool(state.get("active_governance_loop")),
            "no_gate_bypass": not bool(state.get("current_gate")),
            "protected_rules_unchanged": proposal.selected_action.value
            not in {
                "approve_case",
                "select_materiality",
                "select_2lod",
                "change_profile",
                "bypass_gate",
                "publish_external",
            },
            "profile_permitted": bool(
                contract is None
                or state.get("autonomy_profile", "human_governed") in contract.allowed_profiles
            ),
            "external_authority_satisfied": bool(
                contract is None
                or contract.authority_class.value != "CONSEQUENTIAL_EXTERNAL_ACTION"
                or (supervisor.external_write_permitted and contract.human_approval_required)
            ),
        }
        authorised = all(checks.values())
        if authorised:
            decision = "AUTHORISED"
            reason = "All deterministic action, tool, version, budget and authority checks passed."
        elif supervisor.human_decision_required:
            decision = "HUMAN_AUTHORITY_REQUIRED"
            reason = supervisor.governance_reason or "AIRO authority is required before execution."
        else:
            decision = "REJECTED"
            failed = ", ".join(name for name, passed in checks.items() if not passed)
            reason = f"Deterministic authorisation failed: {failed}."
        return ActionAuthorisation(
            authorisation_id=f"AUTH-{uuid.uuid4().hex[:12].upper()}",
            action=proposal.selected_action.value,
            tool=proposal.selected_tool,
            decision=decision,
            reason=reason,
            checks=checks,
            policy_version=supervisor.policy_version,
            case_state_version=int(state.get("case_state_version", 1)),
            rule_version=str(state.get("rule_version", "unknown")),
            timestamp=datetime.now(UTC).isoformat(),
        )
