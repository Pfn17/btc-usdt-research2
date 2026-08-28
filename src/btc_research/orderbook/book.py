from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal

from btc_research.marketdata.types import DepthUpdate, PriceLevel


@dataclass
class OrderBook:
    """In-memory Binance Futures depth book rebuilt from REST plus diff updates."""

    bids: dict[Decimal, Decimal] = field(default_factory=dict)
    asks: dict[Decimal, Decimal] = field(default_factory=dict)
    last_update_id: int | None = None

    @classmethod
    def from_snapshot(
        cls, last_update_id: int, bids: list[PriceLevel], asks: list[PriceLevel]
    ) -> "OrderBook":
        book = cls()
        book._replace_side(book.bids, bids)
        book._replace_side(book.asks, asks)
        book.last_update_id = last_update_id
        return book

    @staticmethod
    def _replace_side(target: dict[Decimal, Decimal], levels: list[PriceLevel]) -> None:
        target.clear()
        for level in levels:
            quantity = Decimal(level.quantity)
            if quantity != 0:
                target[Decimal(level.price)] = quantity

    @staticmethod
    def _apply_side(target: dict[Decimal, Decimal], levels: object) -> None:
        for level in levels:  # type: ignore[union-attr]
            price = Decimal(level.price)
            quantity = Decimal(level.quantity)
            if quantity == 0:
                target.pop(price, None)
            else:
                target[price] = quantity

    def apply(self, update: DepthUpdate, *, bootstrap: bool = False) -> None:
        """Apply a Futures diff, with a special validation path for the first event."""
        if self.last_update_id is None:
            raise ValueError("book is not initialized")

        if update.final_update_id < self.last_update_id:
            return

        if bootstrap:
            if not (
                update.first_update_id <= self.last_update_id <= update.final_update_id
                or update.previous_update_id == self.last_update_id
            ):
                raise ValueError(
                    f"snapshot overlap invalid: last={self.last_update_id}, "
                    f"got {update.first_update_id}-{update.final_update_id} pu={update.previous_update_id}"
                )
        elif update.previous_update_id is not None:
            if update.previous_update_id != self.last_update_id:
                raise ValueError(
                    f"sequence chain gap: expected pu={self.last_update_id}, "
                    f"got pu={update.previous_update_id} for {update.first_update_id}-{update.final_update_id}"
                )
        elif update.first_update_id > self.last_update_id + 1:
            raise ValueError(
                f"sequence gap: expected <= {self.last_update_id + 1}, "
                f"got {update.first_update_id}-{update.final_update_id}"
            )

        self._apply_side(self.bids, update.bids)
        self._apply_side(self.asks, update.asks)
        self.last_update_id = update.final_update_id

    def best_bid(self) -> tuple[Decimal, Decimal] | None:
        return max(self.bids.items()) if self.bids else None

    def best_ask(self) -> tuple[Decimal, Decimal] | None:
        return min(self.asks.items()) if self.asks else None

    def crossed(self) -> bool:
        bid = self.best_bid()
        ask = self.best_ask()
        return bool(bid and ask and bid[0] >= ask[0])
