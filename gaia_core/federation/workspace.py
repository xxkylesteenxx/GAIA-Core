from __future__ import annotations

from gaia_core.models import DissentRecord, WorkspaceState, utcnow


class CollectiveWorkspace:
    def __init__(self, workspace_id: str, problem_frame: str, goals: list[str]) -> None:
        self.state = WorkspaceState(
            workspace_id=workspace_id,
            epoch=1,
            problem_frame=problem_frame,
            goals=goals,
            commitments=[],
        )

    def add_commitment(self, text: str) -> None:
        self.state.commitments.append(text)
        self.state.epoch += 1
        self.state.updated_at = utcnow()

    def preserve_dissent(
        self, core: str, claim: str, confidence: float, rationale: str
    ) -> None:
        self.state.dissent.append(
            DissentRecord(core=core, claim=claim, confidence=confidence, rationale=rationale)
        )
        self.state.epoch += 1
        self.state.updated_at = utcnow()

    def snapshot(self) -> WorkspaceState:
        return self.state
