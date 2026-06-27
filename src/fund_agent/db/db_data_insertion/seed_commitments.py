from decimal import Decimal
from seed_helper import uid
from fund_agent.models.commitment import Commitment
from fund_agent.models.investor import Investor
from fund_agent.models.closing import Closing


LP_COMMITMENT_AMOUNTS = [
    25_000_000, 30_000_000, 20_000_000, 35_000_000,
    15_000_000, 10_000_000, 12_000_000,  5_000_000,
    18_000_000,  8_000_000, 14_000_000,  6_000_000,
]

CLOSE_ASSIGNMENT = [0] * 7 + [1] * 3 + [2] * 2

GP_COMMITMENT_AMOUNT = 3_800_000


def seed_commitments(cur, fund_id, investors: list[Investor], closings: list[Closing]) -> list[Commitment]:
    commitments = []

    commitments.append(_commitment_builder(
        fund_id=fund_id,
        investor_id=investors[0].id,
        closing_id=closings[0].id,
        commitment_amount=GP_COMMITMENT_AMOUNT,
        commitment_date=closings[0].closing_date,
    ))

    for i, (investor, amount) in enumerate(zip(investors[1:], LP_COMMITMENT_AMOUNTS)):
        close_index = CLOSE_ASSIGNMENT[i]
        commitments.append(_commitment_builder(
            fund_id=fund_id,
            investor_id=investor.id,
            closing_id=closings[close_index].id,
            commitment_amount=amount,
            commitment_date=closings[close_index].closing_date,
        ))

    _insert_commitments(cur, commitments)
    return commitments


def _commitment_builder(
    fund_id: str,
    investor_id: str,
    closing_id: str,
    commitment_amount: int,
    commitment_date,
) -> Commitment:
    return Commitment(
        id=uid(),
        fund_id=fund_id,
        investor_id=investor_id,
        closing_id=closing_id,
        commitment_amount=Decimal(str(commitment_amount)),
        commitment_date=commitment_date,
    )


def _insert_commitments(cur, commitments: list[Commitment]) -> None:
    cur.executemany(
        """
        INSERT INTO commitments
            (id, fund_id, investor_id, closing_id, commitment_amount, commitment_date)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        [
            (c.id, c.fund_id, c.investor_id, c.closing_id, c.commitment_amount, c.commitment_date)
            for c in commitments
        ],
    )
