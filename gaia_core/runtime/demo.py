from __future__ import annotations

import json
from datetime import datetime, timezone, timedelta

from gaia_core.bootstrap import build_default_gaia
from gaia_core.grounding.environment import normalize_observation
from gaia_core.models import ObservationSourceClass


def main() -> None:
    gaia = build_default_gaia(".gaia_demo_state")

    terra_obs = normalize_observation(
        source_id="terra-station-01",
        domain="TERRA",
        payload={"temperature_c": 28.4, "soil_moisture": 0.18, "wildfire_risk": 0.74},
        source_class=ObservationSourceClass.FIELD,
        observed_at=datetime.now(timezone.utc) - timedelta(minutes=4),
    )

    aero_obs = normalize_observation(
        source_id="aero-station-09",
        domain="AERO",
        payload={"pm25": 19.0, "wind_mps": 7.1, "pressure_hpa": 1008.2},
        source_class=ObservationSourceClass.LOW_COST_IOT,
        observed_at=datetime.now(timezone.utc) - timedelta(minutes=11),
        adversarial_suspicion=0.08,
    )

    gaia.dispatch("ATLAS", {"kind": "ingest_observation", "payload": {"observation": terra_obs.payload, "domain": terra_obs.domain}})
    gaia.dispatch("ATLAS", {"kind": "ingest_observation", "payload": {"observation": aero_obs.payload, "domain": aero_obs.domain}})
    gaia.dispatch("NEXUS", {"kind": "synchronize", "payload": {"targets": ["TERRA", "AERO", "SOPHIA"]}})
    gaia.dispatch("SOPHIA", {"kind": "summarize", "payload": {"question": "Summarize current terrestrial and atmospheric signals with uncertainty."}})

    gaia.workspace.preserve_dissent(
        "VITA",
        "Biodiversity impact cannot be inferred from current sparse signals alone.",
        0.77,
        "Insufficient species and habitat data.",
    )

    ckpt = gaia.checkpoint()
    snapshot = gaia.consciousness_snapshot()

    print(json.dumps({
        "checkpoint":          ckpt,
        "workspace_epoch":     snapshot["workspace"]["epoch"],
        "memory_event_count":  snapshot["memory_event_count"],
        "cgi":                 snapshot["evidence"]["composite_cgi"],
        "notes":               snapshot["evidence"]["notes"],
    }, indent=2))


if __name__ == "__main__":
    main()
