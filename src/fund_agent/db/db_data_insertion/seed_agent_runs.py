import json
import random
from datetime import date

from seed_helper import uid, d
from fund_agent.models.agent_run import AgentRun


RUN_DATES = [
    date(2021, 9, 1),  date(2021, 11, 1), date(2022, 2, 1),  date(2022, 5, 1),
    date(2022, 8, 1),  date(2022, 11, 1), date(2023, 2, 1),  date(2023, 5, 1),
    date(2023, 8, 1),  date(2023, 11, 1), date(2024, 2, 1),  date(2024, 5, 1),
    date(2024, 8, 1),  date(2024, 11, 1), date(2025, 2, 1),
]

RESERVE_REQUIREMENT = 2_000_000
TOTAL_COMMITTED = 201_800_000
MODEL_VERSION = "claude-opus-4"


def seed_agent_runs(cur) -> list[AgentRun]:
    runs = []
    for run_date in RUN_DATES:
        runs.append(_run_builder(run_date))
    _insert_runs(cur, runs)
    return runs


def _run_builder(run_date: date) -> AgentRun:
    # NOTE: random calls stay in this order (cash, pipeline, trigger, confidence)
    # so the orchestrator's random.seed(...) reproduces the same data each run.
    cash = random.randint(5_000_000, 25_000_000)
    pipeline = random.randint(0, 40_000_000)
    trigger = random.choice(["scheduled", "manual"])
    confidence = d(random.uniform(0.80, 0.97))

    return AgentRun(
        id=uid(),
        trigger=trigger,
        started_at=f"{run_date}T09:00:00+00:00",
        inputs_snapshot={
            "cash_balance": cash,
            "pipeline_obligations": pipeline,
            "reserve_requirement": RESERVE_REQUIREMENT,
            "total_committed": TOTAL_COMMITTED,
        },
        rationale={
            "analysis": f"Cash ${cash:,} vs pipeline ${pipeline:,}",
            "recommendation": "capital_call" if pipeline > cash else "no_action",
        },
        confidence=confidence,
        model_version=MODEL_VERSION,
    )


def _insert_runs(cur, runs: list[AgentRun]) -> None:
    cur.executemany(
        """
        INSERT INTO agent_runs
            (id, trigger, started_at, inputs_snapshot,
             rationale, confidence, model_version)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                r.id, r.trigger, r.started_at,
                json.dumps(r.inputs_snapshot), json.dumps(r.rationale),
                r.confidence, r.model_version,
            )
            for r in runs
        ],
    )
