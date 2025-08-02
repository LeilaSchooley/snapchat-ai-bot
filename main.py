import os
import json
import random
import time
import traceback
from typing import List, Dict, Optional

import uiautomator2 as u2
from faker import Faker

from config import (
    format_prompt,
    PROPOSAL,
    OPENAI_API_KEY,
    PAYPAL_PRODUCT_PRICE,
    IMAGE_FILE_PATH,
    IGNORED_MESSAGES,
    IGNORED_CONTACTS,
    MAX_INVITES_SENT,
    CONTACTS_FILE,
    DEVICE_SERIAL,
    APP_PACKAGE,
    APP_ACTIVITY,
)
from tools import tools, send_invoice_to_user, check_invoice_status

import openai

# Initialize device and services
device = u2.connect(DEVICE_SERIAL) if DEVICE_SERIAL else u2.connect()
client = openai.OpenAI(api_key=OPENAI_API_KEY)
fake = Faker()


def setup_device():
    """Initialize device and start Snapchat app"""
    print("Setting up device...")
    device.screen_on()
    device.app_start(APP_PACKAGE, APP_ACTIVITY)
    time.sleep(3)
    d(resourceId="android:id/button1").click()
    print("Snapchat app started")


def wait_for_element(selector, timeout=10):
    """Wait for element to appear with timeout"""
    try:
        return device(selector).wait(timeout=timeout)
    except Exception as e:
        print(f"Error waiting for element: {e}")
        traceback.print_exc()
        return False


def type_text_naturally(text: str, element):
    """Type text with natural delays"""

    time.sleep(0.5)

    # Clear the field first
    element.clear_text()

    # Build text character by character
    current_text = ""
    for char in text:
        current_text += char
        element.set_text(current_text)
        time.sleep(random.uniform(0.05, 0.15))

    time.sleep(0.5)


def add_contacts():
    """Add new contacts from search"""
    try:
        with open(CONTACTS_FILE, "r") as f:
            added_contacts = f.read().strip().split("\n")
    except FileNotFoundError:
        added_contacts = []

    if len(added_contacts) >= MAX_INVITES_SENT:
        print("Already sent max invites.")
        return

    print("Adding more friends...")

    # Navigate to add friends
    if device(text="Add Friends").exists:
        device(text="Add Friends").click()
    elif device(description="Add Friends").exists:
        device(description="Add Friends").click()
    else:
        print("Could not find Add Friends button")
        return

    time.sleep(2)

    # Find search input
    search_elements = [
        device(resourceId="com.snapchat.android:id/search_input"),
        device(className="android.widget.EditText"),
        device(text="Search"),
    ]

    search_input = None
    for element in search_elements:
        if element.exists:
            search_input = element
            break

    if not search_input:
        print("Could not find search input")
        return

    # Generate random search term
    name = fake.first_name()
    name_prefix = name[:random.randrange(3, 8)]
    print(f'Searching for "{name_prefix}"...')

    type_text_naturally(name_prefix, search_input)
    time.sleep(2)
    current_idx = 0
    while current_idx < 10:  # Limit to 10 attempts per search
        try:
            if len(added_contacts) >= MAX_INVITES_SENT:
                break

            # Get current list of "Add" buttons using list-like API
            add_buttons = device(resourceId="add-friend-button")
            print(add_buttons)
            # Check if we have any add buttons at all
            if add_buttons.count == 0:
                print("No 'Add' buttons found.")
                break

            if current_idx >= add_buttons.count:
                print("No more 'Add' buttons found.")
                break

            # Use list-like access to get the specific button
            add_button = add_buttons[current_idx]

            username = f"user_{current_idx}_{name_prefix}"
            print(f"Trying to add {username}...")

            if add_button.exists:
                add_button.click()
                added_contacts.append(username)
                time.sleep(1)
            else:
                print(f"'Add' button at index {current_idx} no longer exists.")

        except Exception as e:
            print(f"Error adding contact {current_idx}: {e}")
            traceback.print_exc()
            break

        current_idx += 1

    # Save updated contacts list
    with open(CONTACTS_FILE, "w") as f:
        f.write("\n".join(added_contacts))

    print(f"Tried adding {current_idx} contacts")

    # Go back to main screen
    device.press("back")
    time.sleep(1)


def get_contacts() -> List[Dict[str, str]]:
    """Get list of contacts from chat list"""
    contacts = []

    # Navigate to chats
    if device(text="Chat").exists:
        device(text="Chat").click()
    elif device(description="Chat").exists:
        device(description="Chat").click()

    time.sleep(2)

    # Scroll through chat list to find contacts
    for _ in range(3):  # Scroll a few times to get more contacts
        # Look for chat items
        chat_items = device(description="com.snapchat.android:id/chat_item").all()

        for item in chat_items:
            try:
                # Get contact name
                name_element = item.child(className="android.widget.TextView")
                if name_element.exists:
                    contact_name = name_element.get_text()

                    if contact_name not in IGNORED_CONTACTS:
                        contacts.append({
                            "name": contact_name,
                            "element": item
                        })
            except Exception as e:
                print(f"Error processing chat item: {e}")
                traceback.print_exc()
                continue

        # Scroll down for more contacts
        device.swipe(500, 800, 500, 400, 0.5)
        time.sleep(1)

    return contacts


def open_contact(contact: Dict[str, str]) -> bool:
    """Open chat with specific contact"""
    try:
        contact["element"].click()
        time.sleep(2)
        return True
    except Exception as e:
        print(f"Error opening contact {contact.get('name', 'Unknown')}: {e}")
        traceback.print_exc()
        return False


def get_conversation(contact_name: str) -> List[str]:
    """Extract conversation messages from chat"""
    print(f"Getting conversation with {contact_name}...")

    conversation_lines = []

    # Look for message containers

    message_selector = device(resourceId="com.snapchat.android:id/0_resource_name_obfuscated")


    if message_selector.exists:

        for msg in message_selector:
            try:
                text = msg.get_text()
                if text and text not in IGNORED_MESSAGES:
                    conversation_lines.append(text)
            except Exception as e:
                print(f"Error getting message text: {e}")
                traceback.print_exc()
                continue

        return conversation_lines[-10:]  # Return last 10 messages


def parse_conversation(conversation_lines: List[str]) -> List[Dict[str, str]]:
    """Parse conversation lines into message format"""
    messages = []

    # Simple parsing - alternate between user and assistant
    # In real implementation, you'd need to detect message senders
    for i, line in enumerate(conversation_lines):
        role = "user" if i % 2 == 0 else "assistant"
        messages.append({"role": role, "content": line})

    return messages[-8:]


def send_message(message: str):
    """Send a text message"""
    # Find message input
    input_elements = [
        device(resourceId="com.snapchat.android:id/message_input"),
        device(className="android.widget.EditText"),
        device(text="Send a chat"),
    ]

    message_input = None
    for element in input_elements:
        if element.exists:
            message_input = element
            break

    if not message_input:
        print("Could not find message input")
        return False

    type_text_naturally(message, message_input)

    # Find and click send button
    send_buttons = [
        device(resourceId="com.snapchat.android:id/send_button"),
        device(text="Send"),
        device(description="Send"),
    ]

    for button in send_buttons:
        if button.exists:
            button.click()
            time.sleep(1)
            return True

    # If no send button found, try pressing enter
    device.press("enter")
    time.sleep(1)
    return True


def send_image_with_message(image_path: str, message: str):
    """Send an image with accompanying message"""
    if not os.path.exists(image_path):
        print(f"Image file not found: {image_path}")
        return False

    # Look for camera/media button
    media_buttons = [
        device(resourceId="com.snapchat.android:id/camera_button"),
        device(description="Camera"),
        device(text="Camera"),
    ]

    for button in media_buttons:
        if button.exists:
            button.click()
            break
    else:
        print("Could not find camera button")
        return False

    time.sleep(2)

    # Look for gallery/photos option
    if device(text="Photos").exists:
        device(text="Photos").click()
    elif device(description="Gallery").exists:
        device(description="Gallery").click()

    time.sleep(2)

    # This is simplified - in reality you'd need to navigate to the specific image
    # For now, just send the text message
    device.press("back")
    time.sleep(1)
    return send_message(message)


def chat_more(contact_name: str):
    """Generate and send AI response to contact"""
    print(f"Chatting with {contact_name}...")

    conversation_lines = get_conversation(contact_name)
    conversation = parse_conversation(conversation_lines)

    # Don't send if last message was from us
    if conversation and conversation[-1]["role"] == "assistant":
        return

    messages = [
        {
            "role": "system",
            "content": format_prompt(
                price=PAYPAL_PRODUCT_PRICE,
                contact=contact_name,
            ),
        },
        {"role": "user", "content": "Hello! What do you have to offer?"},
        *conversation,
    ]

    if len(conversation) == 0:
        print("No messages sent yet. Sending proposal.")
        # Try to send image with proposal
        if IMAGE_FILE_PATH and os.path.exists(IMAGE_FILE_PATH):
            send_image_with_message(IMAGE_FILE_PATH, PROPOSAL)
        else:
            send_message(PROPOSAL)
    else:
        print("Generating GPT response...")
        try:
            response = client.chat.completions.create(
                model="gpt-4o", messages=messages, tools=tools
            )
            response = response.choices[0].message
            messages.append(response)

            if response.content:
                send_message(response.content)

            if response.tool_calls:
                for tool_call in response.tool_calls:
                    fn_args = json.loads(tool_call.function.arguments)
                    fn_name = tool_call.function.name

                    match fn_name:
                        case "send_invoice_to_user":
                            result = send_invoice_to_user(
                                fn_args.get("user_name", "User"),
                                fn_args.get("user_email", "user@example.com"),
                            )
                            content = json.dumps(result)

                        case "check_invoice_status":
                            result = check_invoice_status(fn_args.get("invoice_id", "NULL"))
                            content = json.dumps(result)

                        case _:
                            content = json.dumps(
                                {"error_message": "Invalid function call."}
                            )

                    messages.append(
                        {
                            "role": "tool",
                            "content": content,
                            "tool_call_id": tool_call.id,
                        }
                    )

                    response = (
                        client.chat.completions.create(
                            model="gpt-4o", messages=messages, tools=tools
                        )
                        .choices[0]
                        .message
                    )

                    if response.content:
                        send_message(response.content)

        except Exception as e:
            print(f"Error generating response: {e}")
            traceback.print_exc()

    print("Sent response")


def main():
    """Main bot loop"""
    setup_device()

    # print("Please manually log into Snapchat and press Enter to continue...")
    # input()

    while True:
        try:
            # Add new contacts
            add_contacts()

            # Get current contacts
            contacts = get_contacts()

            # Chat with each contact
            for contact in contacts:
                contact_name = contact["name"]

                if open_contact(contact):
                    chat_more(contact_name)

                    # Go back to chat list
                    device.press("back")
                    time.sleep(1)

            print("Cooling down for 30 seconds...\n\n")
            time.sleep(30)  # Longer delay for mobile app

        except Exception as e:
            print(f"Error in main loop: {e}")
            traceback.print_exc()
            time.sleep(10)
        except KeyboardInterrupt:
            print("Bot stopped by user")
            break


if __name__ == "__main__":
    main()
