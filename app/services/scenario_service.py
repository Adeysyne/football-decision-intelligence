from datetime import datetime, timezone
from uuid import uuid4

from app.models.scenario import ScenarioCreate, ScenarioResponse


def create_scenario(
    scenario: ScenarioCreate,
) -> ScenarioResponse:
    """
    Create the initial validated representation of a tactical scenario.

    Database persistence will be added in a later production batch.
    """

    return ScenarioResponse(
        scenario_id=uuid4(),
        status="validated",
        created_at=datetime.now(timezone.utc),
        scenario=scenario,
        next_step="decision_engine",
    )