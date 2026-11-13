"""Commission arithmetic with no invented inputs (MN-1..MN-7)."""
from __future__ import annotations

from dataclasses import dataclass, field

DEDUCTIONS = (
    "shipping", "gift_wrapping", "handling", "taxes", "service_charges",
    "credits", "rebates", "card_processing", "bad_debt",
)


@dataclass
class OrderMoney:
    gross_charged: float
    deductions: dict[str, float] = field(default_factory=dict)

    @property
    def qualifying_revenue(self) -> float:
        """Qualifying Revenue = what Amazon actually receives, less the listed items (AT-6)."""
        unknown = set(self.deductions) - set(DEDUCTIONS)
        if unknown:
            raise ValueError(f"unrecognised deduction(s): {sorted(unknown)}")
        out = self.gross_charged - sum(self.deductions.values())
        return max(0.0, round(out, 2))


class RateNotAvailable(Exception):
    """Raised when a commission rate has not been read from the account's rate card."""


def commission(revenue: float, rate_pct: float | None) -> float:
    if rate_pct is None:
        raise RateNotAvailable(
            "No official public rate exists (see flag F-04); refusing to assume a percentage."
        )
    return round(revenue * rate_pct / 100.0, 2)


def payout_ready(balance_usd: float, method: str) -> tuple[bool, float]:
    """Payment minimums from the Program Policies payment chart (MN-5..MN-7)."""
    minimums = {"direct_deposit": 10.0, "gift_card": 10.0, "check": 100.0}
    if method not in minimums:
        raise ValueError(f"unknown payment method {method!r}")
    minimum = minimums[method]
    return balance_usd >= minimum, minimum


def effective_rate_note(rate_pct: float, order_count: int, currency_decimals: int = 2) -> str:
    """MN-3: per-order rounding means the realised rate can differ from the card."""
    return (
        f"With {order_count} orders rounded to {currency_decimals} decimal places, the effective "
        f"rate may differ slightly from the {rate_pct}% rate card figure."
    )
