import urllib.request
import urllib.parse
from django.conf import settings

def send_line_notify(message):
    """
    Send notification to Line Notify.
    """
    token = getattr(settings, 'LINE_NOTIFY_TOKEN', '')
    if not token:
        # Token not configured
        return False
        
    url = 'https://notify-api.line.me/api/notify'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = urllib.parse.urlencode({'message': message}).encode('utf-8')
    
    try:
        req = urllib.request.Request(url, data=data, headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            return response.status == 200
    except Exception as e:
        print(f"Error sending Line Notify: {e}")
        return False
