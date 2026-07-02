from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP
from typing import Sequence

CENT = Decimal("0.01")


def money(value: str | int | Decimal) -> Decimal:
    if isinstance(value, float):
        raise TypeError(f"money() does not accept float ({value!r}); pass a str, int, or Decimal instead")
    return Decimal(value).quantize(CENT, rounding=ROUND_HALF_UP)


def allocate_pro_rata(total: str | int | Decimal, weights: Sequence[str | int | Decimal]) -> list[Decimal]:
    """Split `total` across `weights` so the parts sum exactly to `total`.

    Naive per-share rounding can land a penny off the total; this uses the
    largest-remainder method (floor every share, then hand the leftover cents
    to the shares with the biggest truncated remainder) so allocations always
    tie out exactly.
    """
    total = money(total)
    weights = [w if isinstance(w, Decimal) else money(w) for w in weights]

    if not weights:
        return []
    if any(w < 0 for w in weights):
        raise ValueError("allocate_pro_rata: weights must be non-negative")
    weight_sum = sum(weights)
    if weight_sum == 0:
        raise ValueError("allocate_pro_rata: weights sum to zero")

    raw_shares = [total * w / weight_sum for w in weights]
    floored = [s.quantize(CENT, rounding=ROUND_DOWN) for s in raw_shares]

    leftover_cents = int((total - sum(floored)) / CENT)
    by_remainder = sorted(range(len(weights)), key=lambda i: raw_shares[i] - floored[i], reverse=True)

    shares = list(floored)
    for i in by_remainder[:leftover_cents]:
        shares[i] += CENT
    return shares
