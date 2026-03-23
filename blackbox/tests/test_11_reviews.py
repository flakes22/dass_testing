from conftest import assert_json_response, user_headers


USER_ID = 12


def test_review_rating_out_of_range_rejected(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/products/1/reviews",
        headers=user_headers(USER_ID),
        json={"rating": 6, "comment": "bad rating"},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_review_comment_empty_rejected(base_url):
    import requests

    resp = requests.post(
        f"{base_url}/products/1/reviews",
        headers=user_headers(USER_ID),
        json={"rating": 4, "comment": ""},
        timeout=15,
    )
    assert_json_response(resp, 400)


def test_review_average_must_be_decimal_not_truncated(base_url):
    import requests

    resp = requests.get(
        f"{base_url}/products/1/reviews",
        headers=user_headers(USER_ID),
        timeout=15,
    )
    body = assert_json_response(resp, 200)

    ratings = [r["rating"] for r in body.get("reviews", [])]
    assert len(ratings) > 0

    true_avg = sum(ratings) / len(ratings)
    assert body["average_rating"] == true_avg
