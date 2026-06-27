import random
import json
from seed_helper import uid
from fund_agent.models.investor import Investor


GP = Investor(
    id=uid(),
    legal_name='Apex GP LLC',
    type='GP',
    tax_id='XX-9999999',
    kyc_status='approved',
    banking_ref={'bank': 'JP Morgan', 'account': '****4210'},
    contact={'email': 'gp@apexventures.com'},
)

LP_NAMES = [
    ("Blackrock Alternatives Fund", "institution"),
    ("State Street Pension Trust", "institution"),
    ("Harvard Endowment Management", "institution"),
    ("CalPERS Private Markets", "institution"),
    ("Ontario Teachers Private Equity", "institution"),
    ("Sovereign Capital Partners", "institution"),
    ("Wellington Diversified Fund", "institution"),
    ("Meridian Family Office LLC", "individual"),
    ("Pemberton Capital Group", "institution"),
    ("Horizon Wealth Management", "institution"),
    ("Cascade Asset Management", "institution"),
    ("Sterling Point Advisors", "individual"),
]


def seed_investors(cur) -> list[Investor]:
    investors = [GP]
    for name, investor_type in LP_NAMES:
        investors.append(_seed_lp(name, investor_type))
    _insert_investors(investors, cur)
    return investors


def _seed_lp(investor_name: str, investor_type: str) -> Investor:
    return Investor(
        id=uid(),
        legal_name=investor_name,
        type=investor_type,
        tax_id=f'XX-{random.randint(1000000,9999999)}',
        kyc_status='approved',
        banking_ref={
            'bank': random.choice(['JP Morgan', 'Citi', 'BofA', 'Wells Fargo']),
            'account': f'****{random.randint(1000,9999)}',
        },
        contact={'email': f'ir@{"".join((investor_name.lower().split(" ")[:2]))}.com'},
    )


def _insert_investors(investors: list[Investor], cur) -> None:
    cur.executemany(
        """
        INSERT INTO investors
            (id, legal_name, type, tax_id, kyc_status, banking_ref, contact)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                inv.id, inv.legal_name, inv.type, inv.tax_id, inv.kyc_status,
                json.dumps(inv.banking_ref), json.dumps(inv.contact),
            )
            for inv in investors
        ],
    )
