from datetime import date

from fund_agent.services.money import money


def trial_balance(cur, fund_id: str, as_of: date, investor_id: str | None = None) -> dict:
    """Signed balance per account, replaying all journal lines on or before `as_of`.

    Balances are never stored — they're derived by replaying the ledger up to a
    point in time, which is what lets the system answer "what did this LP's
    capital account look like on March 31" for any date. Reversing entries need
    no special-casing here: a reversal is just another entry, so it nets against
    the original automatically once both are included in the replay.

    `posted` is not a filter here — a held (unposted) entry still represents
    real activity (e.g. an issued capital call) and counts toward the balance.
    `posted` only marks whether cash has been confirmed and the entry is
    therefore locked from further edits; corrections to a posted entry are
    reversing entries, never edits.
    """
    query = """
        SELECT jl.account_id, coa.normal_balance, SUM(jl.debit) AS total_debit, SUM(jl.credit) AS total_credit
        FROM journal_lines jl
        JOIN journal_entries je ON je.id = jl.entry_id
        JOIN chart_of_accounts coa ON coa.id = jl.account_id
        WHERE je.fund_id = %(fund_id)s
          AND je.entry_date <= %(as_of)s
    """
    params = {"fund_id": fund_id, "as_of": as_of}
    if investor_id is not None:
        query += " AND jl.investor_id = %(investor_id)s"
        params["investor_id"] = investor_id
    query += " GROUP BY jl.account_id, coa.normal_balance"

    cur.execute(query, params)

    balances = {}
    for account_id, normal_balance, total_debit, total_credit in cur.fetchall():
        total_debit = money(total_debit)
        total_credit = money(total_credit)
        balances[account_id] = (
            total_debit - total_credit if normal_balance == "debit" else total_credit - total_debit
        )
    return balances
