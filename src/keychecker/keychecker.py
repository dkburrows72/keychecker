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


def check_expiration_and_notify(keys, days_threshold=7):
    for key in keys:
        keytype = key.get("keyType")
        expiry_date_str = key.get("expires")  # Assuming 'expiresAt' field
        if expiry_date_str:
            expiry_date = datetime.datetime.fromisoformat(
                expiry_date_str.replace("Z", "+00:00")
            )
            time_until_expiry = expiry_date - datetime.datetime.now(
                datetime.timezone.utc
            )
            
            log = {"WARNING": f"Tailscale_{keytype}_key_'{key.get('id')}'_expires_in_{time_until_expiry.days}_days."}
            
            if time_until_expiry.days <= days_threshold:
                status = 1    # Fail 
            else:
                status = 0    # Pass
            requests.post(f"https://hc-ping.com/1ae34f92-7d0b-4177-b2a9-3534174a92bc/{status}", timeout=10, data=log)

if __name__ == "__main__":
    api_keys = get_api_keys()
    check_expiration_and_notify(api_keys.get("keys", []))
