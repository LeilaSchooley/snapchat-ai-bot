import traceback

import uiautomator2 as u2

d = u2.connect()

#add_buttons = d(resourceId="add-friend-button")
#print(add_buttons.info)


message_selector = d(resourceId="com.snapchat.android:id/0_resource_name_obfuscated")
conversation_lines = []
if message_selector.exists:

    for msg in message_selector:
        try:
            text = msg.get_text()

            conversation_lines.append(text)
        except Exception as e:
            print(f"Error getting message text: {e}")
            traceback.print_exc()
            continue


print(conversation_lines)