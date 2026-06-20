from seed_helper import uid, d


def seed_fund(cur):
    fund_id = uid()
    cur.execute('''
        INSERT INTO funds
            (id, name, base_currency, vintage_year, fund_term,
             mgmt_fee_rate, hurdle_rate, carry_rate, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ''', (
            fund_id, 'Apex Ventures III, L.P.', 'USD', 2021, 10,
            d(0.0200), d(0.0800), d(0.2000), 'investing',
            ))
    return fund_id
