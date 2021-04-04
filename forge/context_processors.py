from django.conf import settings # import the settings file

def websocket_url(request):
    if (CHAT_SITE_HTTPS):
        url="wss://"+settings.CHAT_SITE_URL+":"+settings.CHAT_SITE_PORT
    else:
        url="ws://"+settings.CHAT_SITE_URL+":"+settings.CHAT_SITE_PORT
    
    return {'SOCKET_URL': url}
