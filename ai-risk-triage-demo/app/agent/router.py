from __future__ import annotations

from typing import Any

from app.agent.policy import ACTION_INPUTS, ACTION_TO_TOOL
from app.llm.base import LLMClient, LLMRuntimeError
from app.schemas import ActionProposal, ActionType, ToolIdentifier


class BoundedActionRouter:
    """Selects one evidence-preparation action; it never executes or mutates state."""

    def __init__(self, llm: LLMClient):
        self.llm = llm

    @staticmethod
    def _direct(action: ActionType, reason: str) -> ActionProposal:
        return ActionProposal(
            selected_action=action,
            selected_tool=ACTION_TO_TOOL[action],
            reason=reason,
            inputs_required=ACTION_INPUTS[action],
            confidence=1.0,
            human_review_required=action == ActionType.ESCALATE_TO_AIRO,
        )

    def recommend(
        self,
        state: dict[str, Any],
        allowed_actions: list[ActionType],
        allowed_tools: list[ToolIdentifier],
    ) -> tuple[ActionProposal, bool]:
        if not allowed_actions:
            return self._direct(ActionType.ESCALATE_TO_AIRO, "No permitted action remains."), False
        if len(allowed_actions) == 1:
            return self._direct(
                allowed_actions[0], "The deterministic policy permits exactly one action."
            ), False
        try:
            proposal = self.llm.propose_action(state, allowed_actions, allowed_tools)
            expected_tool = ACTION_TO_TOOL.get(proposal.selected_action)
            expected_inputs = ACTION_INPUTS.get(proposal.selected_action, [])
            expected_human_review = proposal.selected_action == ActionType.ESCALATE_TO_AIRO
            protected_invalid_tool_demo = (
                state.get("demo_controls", {}).get("router_mode") == "non_allowlisted_tool"
            )
            contract_corrected = (
                proposal.inputs_required != expected_inputs
                or proposal.human_review_required != expected_human_review
            )
            if (
                not protected_invalid_tool_demo
                and proposal.selected_action in allowed_actions
                and expected_tool in allowed_tools
            ):
                contract_corrected = contract_corrected or proposal.selected_tool != expected_tool
                # The model may recommend an action, but the governed contract—not
                # the model—binds executable tool, inputs and review requirements.
                proposal = proposal.model_copy(
                    update={
                        "selected_tool": expected_tool,
                        "inputs_required": expected_inputs,
                        "human_review_required": expected_human_review,
                        "reason": (
                            f"{proposal.reason} The approved action contract "
                            "deterministically bound the executable tool and inputs."
                            if contract_corrected
                            else proposal.reason
                        ),
                    }
                )
            elif proposal.selected_action in allowed_actions:
                proposal = proposal.model_copy(
                    update={
                        "inputs_required": expected_inputs,
                        "human_review_required": expected_human_review,
                    }
                )
            return proposal, True
        except (LLMRuntimeError, NotImplementedError, ValueError) as exc:
            # Safe deterministic fallback: choose the first supervisor-ordered action.
            return self._direct(
                allowed_actions[0],
                f"Governed deterministic fallback after router unavailability: {exc}",
            ), True
