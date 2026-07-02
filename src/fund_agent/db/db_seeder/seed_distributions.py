from datetime import date

from seed_helper import uid, d
from fund_agent.models import Distribution, AgentRun


# (distribution_date, total_amount, type, recallable, agent_run_index)
DIST_DEF = [
    (date(2023, 6, 30),  35_000_000, "return_of_capital", False, 7),
    (date(2023, 12, 15), 18_000_000, "gain",              False, 9),
    (date(2024, 3, 31),  12_000_000, "income",            False, 11),
    (date(2024, 9, 30),  25_000_000, "return_of_capital", True,  13),
    (date(2025, 1, 15),  10_000_000, "gain",              False, 14),
]


def seed_distributions(cur, fund_id, agent_runs: list[AgentRun]) -> list[Distribution]:
    distributions = []
    for i, (dist_date, total, dist_type, recallable, run_idx) in enumerate(DIST_DEF):
        distributions.append(_distribution_builder(
            fund_id=fund_id,
            agent_run_id=agent_runs[run_idx].id,
            distribution_number=i + 1,
            dist_date=dist_date,
            total=total,
            dist_type=dist_type,
            recallable=recallable,
        ))
    _insert_distributions(cur, distributions)
    return distributions


def _distribution_builder(
    fund_id: str,
    agent_run_id: str,
    distribution_number: int,
    dist_date: date,
    total: int,
    dist_type: str,
    recallable: bool,
) -> Distribution:
    return Distribution(
        id=uid(),
        fund_id=fund_id,
        agent_run_id=agent_run_id,
        distribution_number=distribution_number,
        distribution_date=dist_date,
        total_amount=d(total),
        type=dist_type,
        recallable=recallable,
        status="issued",
    )


def _insert_distributions(cur, distributions: list[Distribution]) -> None:
    cur.executemany(
        """
        INSERT INTO distributions
            (id, fund_id, agent_run_id, distribution_number,
             distribution_date, total_amount, type, recallable, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                dist.id, dist.fund_id, dist.agent_run_id, dist.distribution_number,
                dist.distribution_date, dist.total_amount, dist.type,
                dist.recallable, dist.status,
            )
            for dist in distributions
        ],
    )
