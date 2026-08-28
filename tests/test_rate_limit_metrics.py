from btc_research.marketdata.rate_limit import RestRateLimiter


def test_rate_limiter_records_binance_weight_header():
    limiter = RestRateLimiter(0)
    limiter.record_response({"X-MBX-USED-WEIGHT-1M": "123"})

    metrics = limiter.metrics()
    assert metrics.last_used_weight_1m == 123
