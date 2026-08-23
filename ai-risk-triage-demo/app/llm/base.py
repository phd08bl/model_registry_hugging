from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, TypeVar

from pydantic import BaseModel

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
