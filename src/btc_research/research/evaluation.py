from __future__ import annotations

from dataclasses import dataclass
import math
from statistics import mean
from typing import Sequence


@dataclass(frozen=True, slots=True)
class EvaluationResult:
    n: int
    accuracy: float
    mean_return: float
    median_return: float
    win_rate: float
    total_return: float
    max_drawdown: float
    sharpe_like: float
    standard_error: float
    ci95_low: float
    ci95_high: float


def evaluate_predictions(returns: Sequence[float]) -> EvaluationResult:
    if not returns:
        raise ValueError("returns cannot be empty")
    values = list(returns)
    avg = mean(values)
    median = sorted(values)[len(values) // 2] if len(values) % 2 else (sorted(values)[len(values)//2-1] + sorted(values)[len(values)//2]) / 2
    wins = sum(v > 0 for v in values)
    equity = 0.0
    peak = 0.0
    max_dd = 0.0
    for r in values:
        equity += r
        peak = max(peak, equity)
        max_dd = max(max_dd, peak - equity)
    variance = sum((v - avg) ** 2 for v in values) / max(len(values) - 1, 1)
    se = math.sqrt(variance / len(values))
    return EvaluationResult(len(values), wins / len(values), avg, median, wins / len(values), sum(values), max_dd, avg / math.sqrt(variance) if variance > 0 else 0.0, se, avg - 1.96 * se, avg + 1.96 * se)


def paired_differences(model_a: Sequence[float], model_b: Sequence[float]) -> list[float]:
    if len(model_a) != len(model_b) or not model_a:
        raise ValueError("paired samples must have equal non-zero length")
    return [a - b for a, b in zip(model_a, model_b)]
