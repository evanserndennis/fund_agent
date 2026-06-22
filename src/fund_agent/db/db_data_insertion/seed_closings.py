from seed_helper import uid
from datetime import date


CLOSING_DATES = [
    date(2021, 6, 30),
    date(2022, 10, 15),
    date(2023, 3, 31),
]

def seed_closings(cur, fund_id, deals=3):
    closings = []
    for deal in range(0, deals):
        closings.append(_closing_builder(fund_id, deal))
    _insert_closings(closings, cur)
    return closings

def _closing_builder(fund_id: str, closing_number: int) -> dict:
    return {
        'id': uid(),
        'fund_id': fund_id,
        'closing_number': closing_number + 1,
        'closing_date': CLOSING_DATES[closing_number],
    }

def _insert_closings(insertion_payload, cur):
    rows = []
    for closing in insertion_payload:
        row = (
            closing['id'],
            closing['fund_id'],
            closing['closing_number'],
            closing['closing_date'],
        )
        rows.append(row)

    cur.executemany('''
            INSERT INTO closings (id, fund_id, closing_number, closing_date)
            VALUES (%s, %s, %s, %s)
        ''', rows)