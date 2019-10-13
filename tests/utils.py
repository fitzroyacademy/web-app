from app import app
from dataforms import CSRFBaseForm

# class CSRFForm(CSRFBaseForm):
#     pass


def make_authorized_call(
    url, user, data=None, expected_status_code=200, follow_redirects=False
):
    s = app.test_client()
    with s.session_transaction() as sess:
        sess["user_id"] = user.id
    response = s.post(url, data=data, follow_redirects=follow_redirects)
    assert response.status_code == expected_status_code

    return response
