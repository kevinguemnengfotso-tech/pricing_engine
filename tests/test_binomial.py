from pricing_engine.binomial import binomial_price
from pricing_engine.black_scholes import black_scholes


def test_european_call_converges_to_bs():
    p = binomial_price(100, 105, 0.05, 0.2, 1.0, n=1000, is_call=True)
    bs = black_scholes(100, 105, 0.05, 0.2, 1.0, 0.0, True)
    assert abs(p - bs) < 0.05


def test_american_put_ge_european_put():
    am = binomial_price(100, 105, 0.05, 0.2, 1.0, n=500, is_call=False, american=True)
    eu = binomial_price(100, 105, 0.05, 0.2, 1.0, n=500, is_call=False, american=False)
    assert am >= eu