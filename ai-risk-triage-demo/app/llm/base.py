from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

from app.llm.prompts import (
    action_proposal_prompt,
    challenge_prompt,
    evidence_extraction_prompt,
)
from app.schemas import (
    ActionProposal,
    ActionType,
    ChallengeResult,
    EvidenceExtraction,
    ToolIdentifier,
)

T = TypeVar("T", bound=BaseModel)


class LLMRuntimeError(RuntimeError):
    """Expected model transport or structured-output failure."""


class LLMClient(ABC):
    runtime_name: str

    @abstractmethod
    def health(self) -> tuple[bool, str]:
        raise NotImplementedError

    @abstractmethod
    def extract_evidence(
        self, questionnaire: dict[str, Any], numbered_evidence: str
    ) -> EvidenceExtraction:
        raise NotImplementedError

    @abstractmethod
    def challenge(self, state: dict[str, Any]) -> ChallengeResult:
        raise NotImplementedError

    @abstractmethod
    def propose_action(
        self,
        state: dict[str, Any],
        allowed_actions: list[ActionType],
        allowed_tools: list[ToolIdentifier],
    ) -> ActionProposal:
        """Recommend one allowlisted evidence action without executing it."""

        raise NotImplementedError

    def runtime_metadata(self) -> dict[str, Any]:
        return {"runtime": self.runtime_name}


class StructuredLLMClient(LLMClient, ABC):
    """Shared governed prompts for providers with typed structured output."""

    @abstractmethod
    def _structured(self, system: str, user: str, response_model: type[T]) -> T:
        raise NotImplementedError

    def extract_evidence(
        self, questionnaire: dict[str, Any], numbered_evidence: str
    ) -> EvidenceExtraction:
        system, user = evidence_extraction_prompt(questionnaire, numbered_evidence)
        return self._structured(system, user, EvidenceExtraction)

    def challenge(self, state: dict[str, Any]) -> ChallengeResult:
        system, user = challenge_prompt(state)
        return self._structured(system, user, ChallengeResult)

    def propose_action(
        self,
        state: dict[str, Any],
        allowed_actions: list[ActionType],
        allowed_tools: list[ToolIdentifier],
    ) -> ActionProposal:
        system, user = action_proposal_prompt(state, allowed_actions, allowed_tools)
        return self._structured(system, user, ActionProposal)
