import requests
import hashlib
import time

def request_token(auth_token, timestamp):
    secret = "iEk21fuwZApXlz93750dmW22pw389dPwOk"
    pattern = "0001110111101110001111010101111011010001001110011000110001000110"
    first = hashlib.sha256((secret + auth_token).encode()).hexdigest()
    second = hashlib.sha256((str(timestamp) + secret).encode()).hexdigest()
    return ''.join([first[i] if c == '0' else second[i] for i, c in enumerate(pattern)])

def register_account(username, password, email):
    base_url = "https://feelinsonice.appspot.com"
    static_token = "m198sOkJEn37DjqZ32lpRu76xmw288xSQ9"
    timestamp = int(time.time())

    token = request_token(static_token, timestamp)

    # Step 1: Register the email + password
    reg = requests.post(f"{base_url}/bq/register", data={
        "req_token": token,
        "timestamp": timestamp,
        "email": email,
        "password": password,
        "age": 19,
        "birthday": "1994-11-27"
    }, headers={"User-agent": "Snapchat/4.1.01 (Nexus 4; Android 18; gzip)"})

    print("Step 1 Response:", reg.text)
    if not reg.json().get("logged"):
        return "Failed to register email"

    # Step 2: Attach username
    token = request_token(static_token, timestamp)  # reuse same timestamp
    regu = requests.post(f"{base_url}/ph/registeru", data={
        "req_token": token,
        "timestamp": timestamp,
        "email": email,
        "username": username
    }, headers={"User-agent": "Snapchat/4.1.01 (Nexus 4; Android 18; gzip)"})

    print("Step 2 Response:", regu.text)
    if not regu.json().get("logged"):
        return "Failed to attach username"

    return "Account successfully registered!"

# Example use
print(register_account("testusername123", "testpassword", "you@example.com"))
