from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True, slots=True)
class FundingBasisState:
    funding_rate: float
    funding_delta: float
    basis_bps: float
    basis_delta_bps: float
    agreement: int


def basis_bps(mark_price: float, index_price: float) -> Optional[float]:
    if index_price <= 0:
        return None
    return (mark_price / index_price - 1.0) * 10_000.0


def build_state(*, funding_rate: float, previous_funding_rate: float, mark_price: float, index_price: float, previous_basis_bps: float) -> Optional[FundingBasisState]:
    basis = basis_bps(mark_price, index_price)
    if basis is None:
        return None
    funding_delta = funding_rate - previous_funding_rate
    basis_delta = basis - previous_basis_bps
    agreement = int(funding_delta != 0 and basis_delta != 0 and funding_delta * basis_delta > 0)
    return FundingBasisState(funding_rate, funding_delta, basis, basis_delta, agreement)
