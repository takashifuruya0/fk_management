from django.conf import settings
from allauth.socialaccount.models import SocialAccount
import requests
import json


def push_line_messange(uid:str, messages:list):
    """push LINE message
    
    Args:
    - uid: LINE ID
    - messages: list of message [dict]
    
    Returns:
    dict
    - status: bool
    - response: dict
    
    """
    url = "https://api.line.me/v2/bot/message/push"
    token = settings.LINE_ACCESS_TOKEN
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = {
        "to": uid,
        "messages": messages
    }
    json_data = json.dumps(data)
    r = requests.post(url, headers=headers, data=json_data)
    return {
        "status": r.status_code == 200,
        "response": r.json(),
    }

