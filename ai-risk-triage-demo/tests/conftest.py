from __future__ import annotations

import pytest

from app.config import Settings
from app.coordinator import CaseCoordinator
from app.llm.mock import MockLLMClient


@pytest.fixture
def coordinator(tmp_path):
    settings = Settings(
        llm_mode="mock",
        case_db_path=str(tmp_path / "cases.db"),
        checkpoint_db_path=str(tmp_path / "checkpoints.db"),
    )
    instance = CaseCoordinator(settings, MockLLMClient())
    yield instance
    instance._checkpoint_connection.close()
