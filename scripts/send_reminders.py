import os
import sys
import requests


API_URL = os.environ["REMINDER_API_URL"]
API_KEY = os.environ["INTERNAL_API_KEY"]


def main():
    print("Starting EMI reminder cron job...")

    response = requests.post(
        API_URL,
        headers={
            "x-api-key": API_KEY
        },
        timeout=60,
    )

    print(f"HTTP Status: {response.status_code}")
    print(f"Response: {response.text}")

    response.raise_for_status()

    print("EMI reminder cron job completed successfully.")


if __name__ == "__main__":
    main()