from seed_helper import uid, d
from fund_agent.models.distribution_allocation import DistributionAllocation
from fund_agent.models.investor import Investor
from fund_agent.models.commitment import Commitment
from fund_agent.models.distribution import Distribution


def seed_distribution_allocations(
    cur,
    distributions: list[Distribution],
    investors: list[Investor],
    commitments: list[Commitment],
) -> list[DistributionAllocation]:
    # Each LP's pro-rata share is computed once, from LP commitments only (the GP is excluded).
    lp_investors = [inv for inv in investors if inv.type != "GP"]
    commitment_by_investor = {c.investor_id: c.commitment_amount for c in commitments}
    lp_amounts = [commitment_by_investor[inv.id] for inv in lp_investors]
    total_lp_commit = sum(lp_amounts)
    basis_pcts = [d(amt / total_lp_commit) for amt in lp_amounts]

    allocations = []
    for dist in distributions:
        for lp, basis_pct in zip(lp_investors, basis_pcts):
            allocations.append(_allocation_builder(
                distribution_id=dist.id,
                investor_id=lp.id,
                basis_pct=basis_pct,
                dist_total=dist.total_amount,
                dist_type=dist.type,
            ))

    _insert_allocations(cur, allocations)
    return allocations


def _allocation_builder(
    distribution_id: str,
    investor_id: str,
    basis_pct,
    dist_total,
    dist_type: str,
) -> DistributionAllocation:
    lp_total = d(float(dist_total) * float(basis_pct))

    # Waterfall split: how the LP's slice divides depends on the distribution type.
    if dist_type == "return_of_capital":
        roc, pref, profit, carry = lp_total, d(0), d(0), d(0)
    elif dist_type == "income":
        roc    = d(0)
        pref   = d(float(lp_total) * 0.60)
        profit = d(float(lp_total) * 0.30)
        carry  = d(float(lp_total) * 0.10)
    else:  # gain
        roc    = d(0)
        pref   = d(float(lp_total) * 0.30)
        profit = d(float(lp_total) * 0.50)
        carry  = d(float(lp_total) * 0.20)

    return DistributionAllocation(
        id=uid(),
        distribution_id=distribution_id,
        investor_id=investor_id,
        return_of_capital=roc,
        pref_return=pref,
        profit=profit,
        gp_carry=carry,
        total=lp_total,
    )


def _insert_allocations(cur, allocations: list[DistributionAllocation]) -> None:
    cur.executemany(
        """
        INSERT INTO distribution_allocations
            (id, distribution_id, investor_id,
             return_of_capital, pref_return, profit, gp_carry, total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                a.id, a.distribution_id, a.investor_id,
                a.return_of_capital, a.pref_return, a.profit, a.gp_carry, a.total,
            )
            for a in allocations
        ],
    )
