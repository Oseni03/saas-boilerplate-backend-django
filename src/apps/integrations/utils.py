from datetime import datetime
from requests_oauthlib import OAuth2Session

def refresh_token(user_integration):
    platform = user_integration.thirdparty
    oauth = OAuth2Session(client_id=platform.client_id, token={
        'access_token': user_integration.access_token,
        'refresh_token': user_integration.refresh_token,
        'token_type': 'Bearer',
        'expires_in': 3600,
        'expires_at': user_integration.expires_at.timestamp()
    })

    # Refresh the token
    token = oauth.refresh_token(platform.token_url, client_secret=platform.client_secret)

    # Update the token in the database
    user_integration.access_token = token['access_token']
    user_integration.refresh_token = token.get('refresh_token', user_integration.refresh_token)
    user_integration.expires_at = datetime.fromtimestamp(token['expires_at'])
    user_integration.save()

    return user_integration.access_token
