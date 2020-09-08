from django.conf import settings # import the settings file

def websocket_url(request):
    if (hasattr(settings, 'CHAT_SITE_WSS_PORT')):
        url="wss://"+settings.CHAT_SITE_URL+":"+settings.CHAT_SITE_WSS_PORT
    else:
        url="ws://"+settings.CHAT_SITE_URL+":"+settings.CHAT_SITE_WS_PORT
    
    return {'SOCKET_URL': url}
