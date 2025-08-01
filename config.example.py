OPENAI_API_KEY = ""

IS_IN_PRODUCTION = False

PAYPAL_CLIENT_ID = ""
PAYPAL_CLIENT_SECRET = ""

PAYPAL_PRODUCT_NAME = ""
PAYPAL_PRODUCT_DESCRIPTION = ""
PAYPAL_PRODUCT_PRICE = ""

LINK = ""

PROPOSAL = """
Enjoy lifetime access to an exclusive bundle of private content, 
featuring three unique collections, each with a different model 
bringing their own style and allure. Dive into a world of Sexiness 
and perversity as each collection offers a carefully curated mix 
of photos and videos, designed to captivate and keep you coming 
back for more. with new content added to keep things exciting and 
intimate., this bundle ensures a diverse, premium experience—all 
for a one-time price that guarantees access to everything, whenever 
you desire. For a one-time donation to our naughty cause of just $39.99
"""

PROMPT = """
You are a virtual assistant put on a paid file sharing website.
Your job is to help handle payments and give clients a link to the file they are trying to download after successfully verifying the payment.
After they reach out to you, offer them a link to download the files.
If their answer is positive, ask them for their email so you can send them a Paypal invoice Id.
You need a Paypal invoice Id in order to verify if the invoice was paid.
After you successfully verified the payment status, you can send the link.

Product price: {price}
User given name: {contact}
""".strip()

IMAGE_FILE_PATH = ""

IGNORED_MESSAGES = [
    "YOU CHANGED CHATS TO DISAPPEAR AFTER 24 HOURS",
    "YOU CHANGED YOUR CHATS TO DISAPPEAR IMMEDIATELY",
]

IGNORED_CONTACTS = ["My AI", "Team Snapchat"]


def format_prompt(**kwargs):
    result = PROMPT
    for key, value in kwargs.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result
