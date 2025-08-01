import uiautomator2 as u2
import time

def setup_device():
    """Setup and verify Android device connection"""
    print("Connecting to Android device...")
    
    # Connect to device
    device = u2.connect()
    
    # Check device info
    info = device.info
    print(f"Device: {info.get('productName', 'Unknown')}")
    print(f"Android Version: {info.get('version', 'Unknown')}")
    print(f"Screen Size: {info.get('displayWidth', 0)}x{info.get('displayHeight', 0)}")
    
    # Install uiautomator service if needed
    try:
        device.service("uiautomator").start()
        print("UIAutomator service started")
    except Exception as e:
        print(f"Error starting UIAutomator service: {e}")
    
    # Check if Snapchat is installed
    apps = device.app_list()
    if "com.snapchat.android" in apps:
        print("Snapchat app found")
    else:
        print("WARNING: Snapchat app not found. Please install it first.")
    
    return device

if __name__ == "__main__":
    setup_device()