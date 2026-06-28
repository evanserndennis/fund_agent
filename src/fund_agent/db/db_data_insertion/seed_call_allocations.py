from seed_helper import uid, d
from fund_agent.models.call_allocation import CallAllocation
from fund_agent.models.investor import Investor
from fund_agent.models.commitment import Commitment
from fund_agent.models.capital_call import CapitalCall


def seed_call_allocations(
    cur,
    capital_calls: list[CapitalCall],
    investors: list[Investor],
    commitments: list[Commitment],
) -> list[CallAllocation]:
    lp_investors = [inv for inv in investors if inv.type != "GP"]
    commitment_by_investor = {c.investor_id: c.commitment_amount for c in commitments}
    lp_amounts = [commitment_by_investor[inv.id] for inv in lp_investors]
    total_lp_commit = sum(lp_amounts)
    basis_pcts = [d(amt / total_lp_commit) for amt in lp_amounts]

    # Track each LP's remaining unfunded balance as calls are made.
    unfunded_tracker = {inv.id: commitment_by_investor[inv.id] for inv in lp_investors}

    allocations = []
    for call in capital_calls:
        for lp, basis_pct in zip(lp_investors, basis_pcts):
            amount = d(float(call.total_amount) * float(basis_pct))
            unfunded_before = unfunded_tracker[lp.id]
            unfunded_after = d(float(unfunded_before) - float(amount))
            unfunded_tracker[lp.id] = unfunded_after

            allocations.append(CallAllocation(
                id=uid(),
                call_id=call.id,
                investor_id=lp.id,
                amount=amount,
                basis_pct=basis_pct,
                unfunded_before=unfunded_before,
                unfunded_after=unfunded_after,
                status="funded",
            ))

    _insert_allocations(cur, allocations)
    return allocations


def _insert_allocations(cur, allocations: list[CallAllocation]) -> None:
    cur.executemany(
        """
        INSERT INTO call_allocations
            (id, call_id, investor_id, amount,
             basis_pct, unfunded_before, unfunded_after, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                a.id, a.call_id, a.investor_id, a.amount,
                a.basis_pct, a.unfunded_before, a.unfunded_after, a.status,
            )
            for a in allocations
        ],
    )
