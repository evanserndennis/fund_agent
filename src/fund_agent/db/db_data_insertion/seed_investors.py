import random
import json
from seed_helper import uid


GP = {
    'id': uid(),
    'legal_name': 'Apex GP LLC',
    'type': 'GP',
    'tax_id': 'XX-9999999',
    'kyc_status': 'approved',
    'banking_ref': {'bank': 'JP Morgan', 'account': '****4210'},
    'contact': {'email': 'gp@apexventures.com'},
}

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

def seed_investors(cur):
    insertion_payload = [GP,]
    for investor in LP_NAMES:
        insertion_payload.append(_seed_lp(investor[0], investor[1]))
    _insert_investors(insertion_payload, cur)
    return insertion_payload
    

def _seed_lp(investor_name: str, investor_type: str) -> dict:
    return {
        'id': uid(),
        'legal_name': investor_name,
        'type': investor_type,
        'tax_id': f'XX-{random.randint(1000000,9999999)}',
        'kyc_status': 'approved',
        'banking_ref': {
            'bank': random.choice(['JP Morgan', 'Citi', 'BofA', 'Wells Fargo']),
            'account': f'****{random.randint(1000,9999)}'
        },
        'contact': {'email': f'ir@{''.join((investor_name.lower().split(' ')[:2]))}.com'},
    }


def _insert_investors(insertion_payload, cur):
    rows = []
    for investor in insertion_payload:
        row = (
            investor['id'],
            investor['legal_name'],
            investor['type'],
            investor['tax_id'],
            investor['kyc_status'],
            json.dumps(investor['banking_ref']),
            json.dumps(investor['contact']),
        )
        rows.append(row)

    cur.executemany("""
        INSERT INTO investors
            (id, legal_name, type, tax_id, kyc_status, banking_ref, contact)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """, rows)
