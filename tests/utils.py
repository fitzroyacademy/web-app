from app import app


def make_authorized_call(url, user, data=None, expected_status_code=200):
    s = app.test_client()
    with s.session_transaction() as sess:
        sess["user_id"] = user.id
    response = s.post(url, data=data)

    assert response.status_code == expected_status_code

    return response