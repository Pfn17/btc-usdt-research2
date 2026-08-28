from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Sequence


@dataclass(frozen=True, slots=True)
class StandardScaler:
    means: tuple[float, ...]
    scales: tuple[float, ...]

    @classmethod
    def fit(cls, x: Sequence[Sequence[float]]) -> "StandardScaler":
        if not x:
            raise ValueError("training data cannot be empty")
        width = len(x[0])
        if width == 0 or any(len(row) != width for row in x):
            raise ValueError("feature matrix must be rectangular")
        means = tuple(sum(row[j] for row in x) / len(x) for j in range(width))
        scales = tuple(max(math.sqrt(sum((row[j] - means[j]) ** 2 for row in x) / len(x)), 1e-12) for j in range(width))
        return cls(means, scales)

    def transform(self, x: Sequence[Sequence[float]]) -> list[list[float]]:
        if any(len(row) != len(self.means) for row in x):
            raise ValueError("feature width does not match scaler")
        return [[(v - m) / s for v, m, s in zip(row, self.means, self.scales)] for row in x]


@dataclass(frozen=True, slots=True)
class LogisticModel:
    weights: tuple[float, ...]
    bias: float
    classes: tuple[int, int] = (-1, 1)

    @classmethod
    def fit(cls, x: Sequence[Sequence[float]], y: Sequence[int], epochs: int = 300, learning_rate: float = 0.05, l2: float = 1e-4) -> "LogisticModel":
        if not x or len(x) != len(y):
            raise ValueError("x and y must be non-empty and aligned")
        if set(y) - {-1, 1} or len(set(y)) < 2:
            raise ValueError("binary labels must contain both -1 and 1")
        width = len(x[0])
        if width == 0 or any(len(row) != width for row in x):
            raise ValueError("feature matrix must be rectangular")
        if epochs <= 0 or learning_rate <= 0 or l2 < 0:
            raise ValueError("invalid training parameters")
        w = [0.0] * width
        b = 0.0
        n = float(len(x))
        for _ in range(epochs):
            gw = [0.0] * width
            gb = 0.0
            for row, target in zip(x, y):
                z = b + sum(a * c for a, c in zip(w, row))
                z = max(-40.0, min(40.0, z))
                p = 1.0 / (1.0 + math.exp(-z))
                t = 1.0 if target == 1 else 0.0
                err = p - t
                gb += err
                for j, value in enumerate(row):
                    gw[j] += err * value
            for j in range(width):
                w[j] -= learning_rate * (gw[j] / n + l2 * w[j])
            b -= learning_rate * gb / n
        return cls(tuple(w), b)

    def predict_proba(self, x: Sequence[Sequence[float]]) -> list[float]:
        if any(len(row) != len(self.weights) for row in x):
            raise ValueError("feature width does not match model")
        out = []
        for row in x:
            z = max(-40.0, min(40.0, self.bias + sum(a * c for a, c in zip(self.weights, row))))
            out.append(1.0 / (1.0 + math.exp(-z)))
        return out

    def predict(self, x: Sequence[Sequence[float]], threshold: float = 0.5) -> list[int]:
        if not 0.0 < threshold < 1.0:
            raise ValueError("threshold must be between 0 and 1")
        return [1 if p >= threshold else -1 for p in self.predict_proba(x)]
