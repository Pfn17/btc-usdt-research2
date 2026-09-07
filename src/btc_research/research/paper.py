from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Direction = Literal["LONG", "SHORT"]


@dataclass(frozen=True)
class PaperFill:
    """A conservative, deterministic fill estimate; never submits an exchange order."""

    direction: Direction
    entry_price: float
    exit_price: float
    quantity: float
    fee_bps_per_side: float = 4.0
    slippage_bps_per_side: float = 0.0

    @property
    def signed_return_bps(self) -> float:
        sign = 1.0 if self.direction == "LONG" else -1.0
        return sign * (self.exit_price - self.entry_price) / self.entry_price * 10_000.0

    @property
    def gross_pnl(self) -> float:
        return self.quantity * self.entry_price * self.signed_return_bps / 10_000.0

    @property
    def cost_bps(self) -> float:
        return 2.0 * (self.fee_bps_per_side + self.slippage_bps_per_side)

    @property
    def net_pnl(self) -> float:
        return self.gross_pnl - self.quantity * self.entry_price * self.cost_bps / 10_000.0

    def as_dict(self) -> dict[str, float | str]:
        return {
            "direction": self.direction,
            "entry_price": self.entry_price,
            "exit_price": self.exit_price,
            "quantity": self.quantity,
            "signed_return_bps": self.signed_return_bps,
            "gross_pnl": self.gross_pnl,
            "cost_bps": self.cost_bps,
            "net_pnl": self.net_pnl,
            "execution_mode": "PAPER_ONLY",
        }


def simulate_fill(
    direction: Direction,
    entry_price: float,
    exit_price: float,
    quantity: float = 1.0,
    fee_bps_per_side: float = 4.0,
    slippage_bps_per_side: float = 0.0,
) -> PaperFill:
    if entry_price <= 0 or exit_price <= 0:
        raise ValueError("prices must be positive")
    if quantity <= 0:
        raise ValueError("quantity must be positive")
    return PaperFill(direction, entry_price, exit_price, quantity, fee_bps_per_side, slippage_bps_per_side)
