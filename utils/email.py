import requests
from flask import current_app


def send_email(email_to, email_from, subject, body):
    message_data = {
        "from": email_from,
        "to": email_to,
        "subject": subject,
        "html": body,
    }
    message_data = {k: v for k, v in message_data.items() if v is not None}

    if not current_app.config.get("MAILGUN_API_URL") or not current_app.config.get(
        "MAILGUN_API_KEY"
    ):
        current_app.logger.warning(
            "No MAILGUN_API_URL or MAILGUN_API_KEY provided. Dumping email contents: {}".format(
                message_data
            )
        )
        return

    response = requests.post(
        "{}/messages".format(current_app.config.get("MAILGUN_API_URL")),
        auth=requests.auth.HTTPBasicAuth(
            "api", current_app.config.get("MAILGUN_API_KEY")
        ),
        data=message_data,
    )
    response.raise_for_status()
    return response
