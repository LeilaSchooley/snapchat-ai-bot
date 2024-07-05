import uiautomator2 as u2
import time
import json

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)

# Connect to the device
d = u2.connect()

# Function to login to Snapchat
def login_to_snapchat(username, password):
    # Launch Snapchat
    d.app_start("com.snapchat.android")

    # Wait for the login screen
    d(text="Log In").wait(timeout=10.0)
    d(text="Log In").click()

    # Enter username
    d(resourceId="com.snapchat.android:id/username_or_email_field").set_text(username)
    d(resourceId="com.snapchat.android:id/password_field").set_text(password)
    d(resourceId="com.snapchat.android:id/button_text").click()

    # Wait for the main screen
    d(resourceId="com.snapchat.android:id/camera_capture_button").wait(timeout=10.0)

# Function to add a friend by username
def add_friend(username):
    # Open the Add Friends screen
    d(resourceId="com.snapchat.android:id/profile_icon").click()
    d(text="Add Friends").click()

    # Search for the username
    d(resourceId="com.snapchat.android:id/search").set_text(username)
    time.sleep(2)  # Wait for the search results to load

    # Add the first result
    d(resourceId="com.snapchat.android:id/add_button").click()

    # Wait for the confirmation
    time.sleep(2)

# Function to send a snap
def send_snap(username, snap_image_path):
    # Go to chat
    d(resourceId="com.snapchat.android:id/chat_icon").click()

    # Search for the username
    d(resourceId="com.snapchat.android:id/search").set_text(username)
    time.sleep(2)  # Wait for the search results to load

    # Open the chat
    d(resourceId="com.snapchat.android:id/avatar_icon").click()

    # Attach and send the snap
    d(resourceId="com.snapchat.android:id/camera_capture_button").click()
    d(resourceId="com.snapchat.android:id/send_btn").click()

    # Confirm the send
    d(resourceId="com.snapchat.android:id/send_to_confirm_btn").click()

    # Wait for the snap to be sent
    time.sleep(2)

# Main function
def main():
    # Login to Snapchat
    login_to_snapchat(config["username"], config["password"])

    # Add friends and send snaps
    friends = ["friend_username1", "friend_username2", "friend_username3"]
    snap_image_path = "/path/to/your/snap/image.jpg"

    for friend in friends:
        add_friend(friend)
        send_snap(friend, snap_image_path)

    # Close Snapchat
    d.app_stop("com.snapchat.android")

if __name__ == "__main__":
    main()
