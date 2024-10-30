import identity.web
from flask import current_app, session, url_for
from msal import ConfidentialClientApplication

def get_auth_instance():
    """Creates and returns an Auth instance based on the current app configuration."""
    return identity.web.Auth(
        session=session,
        authority=current_app.config.get("AUTHORITY"),
        client_id=current_app.config["CLIENT_ID"],
        client_credential=current_app.config["CLIENT_SECRET"],
    )

def get_access_token():
    """Acquires an access token for Microsoft Graph API."""
    client_app = ConfidentialClientApplication(
        client_id=current_app.config["CLIENT_ID"],
        client_credential=current_app.config["CLIENT_SECRET"],
        authority=current_app.config["AUTHORITY"],
    )

    # Attempt silent acquisition first
    result = client_app.acquire_token_silent(scopes=["https://graph.microsoft.com/.default"], account=None)
    if not result:
        # Fall back to client credential acquisition
        result = client_app.acquire_token_for_client(scopes=["https://graph.microsoft.com/.default"])

    if "access_token" in result:
        return result["access_token"]
    else:
        raise ValueError("Failed to acquire token: " + result.get("error_description", "Unknown error"))

def log_in():
    auth = get_auth_instance()
    return auth.log_in(
        scopes=current_app.config["SCOPE"],
        redirect_uri=url_for("auth_response", _external=True),
    )

def complete_log_in(args):
    auth = get_auth_instance()
    return auth.complete_log_in(args)

def log_out(redirect_url):
    auth = get_auth_instance()
    return auth.log_out(redirect_url)

def get_token_for_user():
    auth = get_auth_instance()
    return auth.get_token_for_user(current_app.config["SCOPE"])

def get_user():
    auth = get_auth_instance()
    return auth.get_user()
