import json

from seed_helper import uid
from fund_agent.models import AgentDecision, AgentRun, CapitalCall, Distribution


def seed_agent_decisions(
    cur,
    agent_runs: list[AgentRun],
    capital_calls: list[CapitalCall],
    distributions: list[Distribution],
) -> list[AgentDecision]:
    # Map each run to what it actually produced.
    calls_by_run = {c.agent_run_id: c for c in capital_calls}
    dists_by_run = {d.agent_run_id: d for d in distributions}

    decisions = []
    for run in agent_runs:
        if run.id in calls_by_run:
            call = calls_by_run[run.id]
            decisions.append(_decision_builder(
                run_id=run.id,
                decision_type="call",
                supporting_data={"call_id": call.id, "total_amount": float(call.total_amount), "purpose": call.purpose},
                requires_approval=True,
            ))
        if run.id in dists_by_run:
            dist = dists_by_run[run.id]
            decisions.append(_decision_builder(
                run_id=run.id,
                decision_type="distribution",
                supporting_data={"distribution_id": dist.id, "total_amount": float(dist.total_amount), "type": dist.type},
                requires_approval=True,
            ))
        if run.id not in calls_by_run and run.id not in dists_by_run:
            decisions.append(_decision_builder(
                run_id=run.id,
                decision_type="no_action",
                supporting_data=None,
                requires_approval=False,
            ))

    _insert_decisions(cur, decisions)
    return decisions


def _decision_builder(
    run_id: str,
    decision_type: str,
    supporting_data,
    requires_approval: bool,
) -> AgentDecision:
    return AgentDecision(
        id=uid(),
        run_id=run_id,
        decision_type=decision_type,
        supporting_data=supporting_data,
        requires_approval=requires_approval,
    )


def _insert_decisions(cur, decisions: list[AgentDecision]) -> None:
    cur.executemany(
        """
        INSERT INTO agent_decisions
            (id, run_id, decision_type, supporting_data, requires_approval)
        VALUES (%s, %s, %s, %s, %s)
        """,
        [
            (
                d.id, d.run_id, d.decision_type,
                json.dumps(d.supporting_data), d.requires_approval,
            )
            for d in decisions
        ],
    )
