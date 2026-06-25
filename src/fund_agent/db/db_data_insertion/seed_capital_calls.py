from datetime import date

from seed_helper import uid, d


# (call_date, due_date, total_amount, purpose, agent_run_index)
CALL_DEF = [
    (date(2021, 9, 15),  date(2021, 9, 30),  20_000_000, "investment", 0),
    (date(2021, 11, 15), date(2021, 11, 30), 30_000_000, "investment", 1),
    (date(2022, 2, 15),  date(2022, 3, 1),   25_000_000, "investment", 2),
    (date(2022, 5, 15),  date(2022, 5, 31),  18_000_000, "investment", 3),
    (date(2022, 8, 15),  date(2022, 8, 31),  15_000_000, "investment", 4),
    (date(2022, 11, 15), date(2022, 11, 30), 12_000_000, "investment", 5),
    (date(2023, 2, 15),  date(2023, 3, 1),   10_000_000, "expense",    6),
    (date(2023, 5, 15),  date(2023, 5, 31),  20_000_000, "investment", 7),
    (date(2023, 8, 15),  date(2023, 8, 31),  14_000_000, "investment", 8),
    (date(2023, 11, 15), date(2023, 11, 30),  8_000_000, "fee",        9),
]


def seed_capital_calls(cur, fund_id, agent_runs) -> list[dict]:
    calls = []
    for i, (call_date, due_date, total, purpose, run_idx) in enumerate(CALL_DEF):
        calls.append(_call_builder(
            fund_id=fund_id,
            agent_run_id=agent_runs[run_idx]["id"],
            call_number=i + 1,
            call_date=call_date,
            due_date=due_date,
            total=total,
            purpose=purpose,
        ))
    _insert_calls(cur, calls)
    return calls


def _call_builder(
    fund_id: str,
    agent_run_id: str,
    call_number: int,
    call_date: date,
    due_date: date,
    total: int,
    purpose: str,
) -> dict:
    return {
        "id": uid(),
        "fund_id": fund_id,
        "agent_run_id": agent_run_id,
        "call_number": call_number,
        "call_date": call_date,
        "due_date": due_date,
        "total_amount": d(total),
        "purpose": purpose,
        "status": "funded",
    }


def _insert_calls(cur, calls: list[dict]) -> None:
    cur.executemany(
        """
        INSERT INTO capital_calls
            (id, fund_id, agent_run_id, call_number,
             call_date, due_date, total_amount, purpose, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                c["id"], c["fund_id"], c["agent_run_id"], c["call_number"],
                c["call_date"], c["due_date"], c["total_amount"], c["purpose"], c["status"],
            )
            for c in calls
        ],
    )
