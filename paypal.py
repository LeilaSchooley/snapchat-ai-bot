from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from config import (
    IS_IN_PRODUCTION,
    PAYPAL_CLIENT_ID,
    PAYPAL_CLIENT_SECRET,
    PAYPAL_PRODUCT_NAME,
    PAYPAL_PRODUCT_DESCRIPTION,
    PAYPAL_PRODUCT_PRICE,
)


def get_paypal_api_url(suffix: str):
    if IS_IN_PRODUCTION:
        return f"https://api-m.paypal.com{suffix}"
    return f"https://api-m.sandbox.paypal.com{suffix}"


def generate_access_token():
    # generate api access token
    url = get_paypal_api_url("/v1/oauth2/token")
    auth = HTTPBasicAuth(PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    response = requests.post(url, data={"grant_type": "client_credentials"}, auth=auth)
    response.raise_for_status()
    access_token = response.json()["access_token"]
    return access_token


def generate_invoice_number(access_token: str):
    url = get_paypal_api_url("/v2/invoicing/generate-next-invoice-number")
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json",
        },
    )
    response.raise_for_status()
    invoice_number = response.json()["invoice_number"]
    return invoice_number


def generate_paypal_invoice(
    access_token: str, recipient_name: str, recipient_email: str
):
    url = get_paypal_api_url("/v2/invoicing/invoices")
    invoice_number = generate_invoice_number()
    today = datetime.now().date()
    invoice_date = f"{today.year}-{today.month}-{today.day}"
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Prefer": "return=representation",
        },
        json={
            "detail": {
                "invoice_number": invoice_number,
                "invoice_date": invoice_date,
                "currency_code": "USD",
            },
            "primary_recipients": [
                {
                    "billing_info": {
                        "name": {"given_name": recipient_name},
                        "email_address": recipient_email,
                    },
                }
            ],
            "items": [
                {
                    "name": PAYPAL_PRODUCT_NAME,
                    "description": PAYPAL_PRODUCT_DESCRIPTION,
                    "quantity": "1",
                    "unit_amount": {
                        "currency_code": "USD",
                        "value": PAYPAL_PRODUCT_PRICE,
                    },
                },
            ],
        },
    )
    response.raise_for_status()
    invoice_id = response.json()["id"]
    return invoice_id


def send_invoice(access_token: str, invoice_id: str):
    url = get_paypal_api_url(f"/v2/invoicing/invoices/{invoice_id}/send")
    response = requests.post(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
        json={"send_to_invoicer": True},
    )
    response.raise_for_status()
    return True


def get_invoice_status(access_token: str, invoice_id: str):
    url = get_paypal_api_url(f"/v2/invoicing/invoices/{invoice_id}")
    response = requests.get(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
        },
    )
    response.raise_for_status()
    status = response.json()["status"]
    return status
