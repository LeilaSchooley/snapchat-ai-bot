from paypal import (
    generate_access_token,
    generate_paypal_invoice,
    send_invoice,
    get_invoice_status,
)
from config import LINK


def send_invoice_to_user(user_name: str, user_email: str):
    try:
        access_token = generate_access_token()
        invoice_id = generate_paypal_invoice(access_token, user_name, user_email)
        invoice_sent = send_invoice(access_token, invoice_id)
        return {
            "invoice_id": invoice_id,
            "recipient_given_name": user_name,
            "recipient_email": user_email,
            "invoice_send_success": invoice_sent,
        }
    except Exception as e:
        return {
            "recipient_given_name": user_name,
            "recipient_email": user_email,
            "invoice_send_success": invoice_sent,
            "error_message": str(e),
        }


def check_invoice_status(invoice_id: str):
    try:
        access_token = generate_access_token()
        invoice_status = get_invoice_status(access_token, invoice_id)
        data = {"invoice_id": invoice_id, "invoice_status": invoice_status}
        if invoice_status == "PAID" or invoice_status == "MARKED_AS_PAID":
            data["download_link"] = LINK
        return data
    except Exception as e:
        return {
            "invoice_id": invoice_id,
            "invoice_status": "UNKNOWN",
            "error_message": str(e),
        }


# since some parameters are defined by the configuration, only ask gpt to provide some of the parameters
tools = [
    {
        "type": "function",
        "function": {
            "name": "send_invoice_to_user",
            "description": "Send the invoice to the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_name": {
                        "type": "string",
                        "description": "The given name of the user",
                    },
                    "user_email": {
                        "type": "string",
                        "description": "The email of the user",
                    },
                },
                "required": [
                    "user_name",
                    "user_email",
                ],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "check_invoice_status",
            "description": "Check the current status of the invoice sent to the user",
            "parameters": {
                "type": "object",
                "properties": {
                    "invoice_id": {
                        "type": "string",
                        "description": "The ID of the invoice sent to the user",
                    },
                },
                "required": [
                    "invoice_id",
                ],
            },
        },
    },
]
