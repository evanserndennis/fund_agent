from seed_helper import uid
from datetime import date
from fund_agent.models.closing import Closing


CLOSING_DATES = [
    date(2021, 6, 30),
    date(2022, 10, 15),
    date(2023, 3, 31),
]


def seed_closings(cur, fund_id, deals=3) -> list[Closing]:
    closings = []
    for deal in range(0, deals):
        closings.append(_closing_builder(fund_id, deal))
    _insert_closings(closings, cur)
    return closings


def _closing_builder(fund_id: str, closing_number: int) -> Closing:
    return Closing(
        id=uid(),
        fund_id=fund_id,
        closing_number=closing_number + 1,
        closing_date=CLOSING_DATES[closing_number],
    )


def _insert_closings(closings: list[Closing], cur) -> None:
    cur.executemany(
        """
        INSERT INTO closings (id, fund_id, closing_number, closing_date)
        VALUES (%s, %s, %s, %s)
        """,
        [(c.id, c.fund_id, c.closing_number, c.closing_date) for c in closings],
    )
