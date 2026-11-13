"""Attribution windows from the Commission Income Statement (AT-1..AT-4).

All durations are hours, taken from the policy text quoted in data/program.json.
"""
from __future__ import annotations

from dataclasses import dataclass

SESSION_HOURS = 24          # AT-1
CART_WINDOW_DAYS = 89       # AT-3
FULFILMENT_WINDOW_DAYS = 180  # AT-4


@dataclass(frozen=True)
class Click:
    at_hour: float
    tag_is_own: bool = True


@dataclass(frozen=True)
class Order:
    placed_at_hour: float
    shipped_and_paid_at_hour: float | None
    is_digital: bool = False
    returned: bool = False


def session_open(click: Click, order: Order) -> bool:
    """The session ends at 24h, at an order, or at another associate's click (AT-1/AT-2)."""
    if not click.tag_is_own:
        return False
    return 0 <= (order.placed_at_hour - click.at_hour) <= SESSION_HOURS


def qualifies(click: Click, order: Order) -> tuple[bool, str]:
    if order.returned:
        return False, "DQ-5: order was cancelled, returned or refunded"
    if not session_open(click, order):
        return False, "AT-1: outside the 24-hour session window"
    if (order.placed_at_hour - click.at_hour) > CART_WINDOW_DAYS * 24:
        return False, "AT-3: cart converted more than 89 days after the click"
    if order.is_digital:
        return False, "AT-2: digital products follow a separate rule"
    if order.shipped_and_paid_at_hour is None:
        return False, "AT-4: no shipment/payment record yet"
    if (order.shipped_and_paid_at_hour - order.placed_at_hour) > FULFILMENT_WINDOW_DAYS * 24:
        return False, "AT-4: not shipped and paid within 180 days of purchase"
    return True, "qualifying purchase"
