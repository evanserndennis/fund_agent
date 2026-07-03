import os

from fund_agent.services.money import money

DEFAULT_RESERVE_AMOUNT = money("15000.00")


def get_reserve_amount():
    return money(os.getenv("FUND_RESERVE_AMOUNT", DEFAULT_RESERVE_AMOUNT))
