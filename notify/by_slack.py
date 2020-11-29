"""
Slack app notifier for incoming webhooks

:author: abhinavcreed13
"""
import json
import requests


class SlackAppNotifier:
    """
    Send notification to slack using incoming webhooks.
    """
    def __init__(self, hook_url: str) -> None:
        print("Configuring Slack Notifier...")
        self.hook_url = hook_url

    def notify(self, subject: str, text: str) -> None:
        """Slack webhook notify function
        Args:
            subject(str): subject of the message to post
            text(str): text of the message to post
        Returns:
            None
        Raises:
            Exception: Post request error code and message
        """
        print("Sending message to slack incoming webhook...")
        print("Message:", '"""', text, '"""', sep="\n")

        # create data payload
        slack_data = {
            "text": f"{subject}",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*{subject}*"
                    }
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"{text}"
                    }
                }
            ]
        }

        # post to the webhook
        r = requests.post(self.hook_url,
                          data=json.dumps(slack_data),
                          headers={'Content-Type': 'application/json'})

        # handling post error
        if r.status_code != 200:
            raise Exception(
                f'Request to slack returned an error %s, the response is:\n{r.status_code}, {r.text}')

        print("Sent!", r.text)