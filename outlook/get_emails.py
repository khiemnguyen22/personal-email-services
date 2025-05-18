from main import MS_GRAPH_BASE_URL, get_access_token
from config import CLIENT_ID, CLIENT_SECRET, SCOPES
import httpx
import requests 

def get_recent_email(access_token):
    url = f"{MS_GRAPH_BASE_URL}/me/messages"
    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        emails = response.json().get("value", [])
        if emails:
            latest_email = emails[0]
            print("\n📧 **Latest Email Details:**")
            print("Subject:", latest_email.get("subject"))
            print("From:", latest_email.get("from", {}).get("emailAddress", {}).get("address"))
            print("Received:", latest_email.get("receivedDateTime"))
            print("Snippet:", latest_email.get("bodyPreview"))
        else:
            print("No emails found.")
    else:
        print("Error fetching emails:", response.json())

if __name__ == "__main__":
    try:
        access_token = get_access_token(CLIENT_ID, CLIENT_SECRET, SCOPES)
        get_recent_email(access_token)
    except Exception as e:
        print(e)
