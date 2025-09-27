import configparser
import datetime

import requests

config = configparser.ConfigParser()
config.read("settings.ini")

TAILSCALE_API_KEY = config["keys"]["TAILSCALE_API_KEY"]
TAILSCALE_API_BASE_URL = "https://api.tailscale.com/api/v2/tailnet/"


def get_api_keys():
    headers = {"Authorization": f"Bearer {TAILSCALE_API_KEY}"}
    response = requests.get(
        f"{TAILSCALE_API_BASE_URL}{config['keys']['TAILNET_NAME']}/keys",
        headers=headers,
    )
    response.raise_for_status()
    return response.json()


def check_expiration_and_notify(keys, days_threshold=365):
    for key in keys:
        expiry_date_str = key.get("expires")  # Assuming 'expiresAt' field
        if expiry_date_str:
            expiry_date = datetime.datetime.fromisoformat(
                expiry_date_str.replace("Z", "+00:00")
            )
            time_until_expiry = expiry_date - datetime.datetime.now(
                datetime.timezone.utc
            )

            if time_until_expiry.days <= days_threshold:
                print(
                    f"WARNING: Tailscale API key '{key.get('id')}' expires in {time_until_expiry.days} days."
                )
                # Implement your notification logic here (e.g., send email, Slack message)


if __name__ == "__main__":
    api_keys = get_api_keys()
    check_expiration_and_notify(api_keys.get("keys", []))
