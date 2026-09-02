import pytest

from btc_research.marketdata.ohlcv import BinanceFuturesKlines


def test_parse_kline_rows() -> None:
    rows = [[
        1_000,
        "100.0",
        "101.0",
        "99.5",
        "100.5",
        "12.5",
        60_999,
        "1256.25",
        42,
        "6.5",
        "653.25",
        "0",
    ]]
    candles = BinanceFuturesKlines._parse_rows("BTCUSDT", "1m", rows)
    assert len(candles) == 1
    candle = candles[0]
    assert candle.open_time_ms == 1_000
    assert candle.close_time_ms == 60_999
    assert candle.close == pytest.approx(100.5)
    assert candle.trade_count == 42
    assert candle.taker_buy_volume == pytest.approx(6.5)


def test_historical_rejects_invalid_range() -> None:
    # Validation is synchronous in intent even though the public method is async.
    with pytest.raises(TypeError):
        # Calling without required keyword arguments must fail before any network I/O.
        BinanceFuturesKlines("https://fapi.binance.com").historical("1m")  # type: ignore[call-arg]
