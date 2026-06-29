from seed_helper import uid, d
from fund_agent.models import Fund


def seed_fund(cur) -> Fund:
    fund = Fund(
        id=uid(),
        name='Apex Ventures III, L.P.',
        base_currency='USD',
        vintage_year=2021,
        fund_term=10,
        mgmt_fee_rate=d(0.0200),
        hurdle_rate=d(0.0800),
        carry_rate=d(0.2000),
        status='investing',
    )
    cur.execute(
        """
        INSERT INTO funds
            (id, name, base_currency, vintage_year, fund_term,
             mgmt_fee_rate, hurdle_rate, carry_rate, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            fund.id, fund.name, fund.base_currency, fund.vintage_year, fund.fund_term,
            fund.mgmt_fee_rate, fund.hurdle_rate, fund.carry_rate, fund.status,
        ),
    )
    return fund
