from conftest import assert_json_response, user_headers


USER_ID = 6


def test_products_list_shows_only_active(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/products",
        headers=user_headers(USER_ID),
        timeout=20,
    )
    products = assert_json_response(resp, 200)
    assert isinstance(products, list)
    assert len(products) > 0
    assert all(p.get("is_active") is True for p in products)


def test_get_missing_product_returns_404(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/products/999999",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    assert_json_response(resp, 404)


def test_products_sort_price_ascending(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/products?sort=price_asc",
        headers=user_headers(USER_ID),
        timeout=20,
    )
    products = assert_json_response(resp, 200)
    prices = [p["price"] for p in products]
    assert prices == sorted(prices)
