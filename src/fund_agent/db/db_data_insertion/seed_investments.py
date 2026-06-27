from seed_helper import uid, d
from fund_agent.models.investment import Investment


# (company_name, invested_amount, current_value, realized_proceeds, status)
PORTFOLIO = [
    ("TechCorp Inc.",          35_000_000, 52_000_000,  0,          "active"),
    ("MedDevice Solutions",    28_000_000, 41_500_000,  0,          "active"),
    ("GreenEnergy Systems",    22_000_000, 18_000_000,  0,          "active"),
    ("FinTech Platforms LLC",  18_000_000, 32_000_000,  0,          "active"),
    ("DataStream Analytics",   15_000_000, 28_000_000,  0,          "active"),
    ("CloudBase Inc.",         12_000_000, 12_000_000,  18_000_000, "partially_realized"),
    ("RetailAI Corp",          10_000_000, 14_500_000,  0,          "active"),
    ("BioLab Sciences",         8_000_000,  0,           0,          "written_off"),
    ("Supply Chain Co.",       20_000_000,  0,          35_000_000, "realized"),
    ("PropTech Ventures",      14_000_000, 19_000_000,  0,          "active"),
]


def seed_investments(cur, fund_id) -> list[Investment]:
    investments = []
    for company, invested, current, realized, status in PORTFOLIO:
        investments.append(_investment_builder(fund_id, company, invested, current, realized, status))
    _insert_investments(cur, investments)
    return investments


def _investment_builder(
    fund_id: str,
    company: str,
    invested: int,
    current: int,
    realized: int,
    status: str,
) -> Investment:
    return Investment(
        id=uid(),
        fund_id=fund_id,
        company_name=company,
        invested_amount=d(invested),
        current_value=d(current) if current else None,
        realized_proceeds=d(realized),
        status=status,
    )


def _insert_investments(cur, investments: list[Investment]) -> None:
    cur.executemany(
        """
        INSERT INTO investments
            (id, fund_id, company_name, invested_amount,
             current_value, realized_proceeds, status)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
        """,
        [
            (
                inv.id, inv.fund_id, inv.company_name, inv.invested_amount,
                inv.current_value, inv.realized_proceeds, inv.status,
            )
            for inv in investments
        ],
    )
