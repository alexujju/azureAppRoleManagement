import requests
from flask import current_app
from auth_helper import get_access_token  # Import your token acquisition function
#import jsonify
import logging

def fetch_app_roles():
    token = get_access_token()  # Get the access token for Microsoft Graph API
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{current_app.config['SERVICE_PRINCIPAL']}/appRoles"

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        return response.json()  # Return the list of application roles directly
    else:
        raise ValueError(f"Failed to fetch roles: {response.status_code} {response.text}")
    
def get_user_roles_with_names():
    """
    Fetches user roles with names from Microsoft Graph API.

    Returns:
        A list of user roles with their names, or an error message.
    """
    try:
        # Ensure the SERVICE_PRINCIPAL is set in the config
        service_principal_id = current_app.config.get('SERVICE_PRINCIPAL')
        if not service_principal_id:
            return {"error": "SERVICE_PRINCIPAL not configured."}, 400

        token = get_access_token()
        headers = {"Authorization": f"Bearer {token}"}

        # Step 2: Get app roles from the service principal
        app_roles_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_id}/appRoles"
        roles_response = requests.get(app_roles_url, headers=headers)
        roles_response.raise_for_status()
        app_roles = roles_response.json().get("value", [])

        # Map role IDs to role names for easy lookup
        role_id_to_name = {role["id"]: role["displayName"] for role in app_roles}

        # Step 3: Fetch users and their role assignments
        roles_assignment_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_id}/appRoleAssignedTo"
        assignments_response = requests.get(roles_assignment_url, headers=headers)
        assignments_response.raise_for_status()
        users_with_roles = assignments_response.json().get("value", [])

        # Step 4: Add role name to each user's role assignment
        for user_role in users_with_roles:
            role_id = user_role["appRoleId"]
            user_role["roleName"] = role_id_to_name.get(role_id, "Unknown Role")

        return users_with_roles, 200  # Return the data and status code

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error: {req_err}")
        return {"error": "Failed to fetch data from Microsoft Graph API."}, 500
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {"error": str(e)}, 500
    
def get_role_name_by_id(role_id):
    """
    Fetch the role name by its ID.

    Args:
        role_id (str): The ID of the role.

    Returns:
        The name of the role or "Unknown Role" if not found.
    """
    try:
        roles = fetch_app_roles()  # Assuming this returns a list of roles
        role_id_to_name = {role["id"]: role["displayName"] for role in roles}
        return role_id_to_name.get(role_id, "Unknown Role")
    except Exception as e:
        logging.error(f"Error fetching role name: {e}")
        return "Unknown Role"


def get_user_roles_by_email(email):
    """
    Fetches roles assigned to a user by their email address.

    Args:
        email (str): The email address of the user.

    Returns:
        A list of dictionaries containing user name, email, application display name, role name, and assignment date.
    """
    try:
        # Get the access token
        token = get_access_token()
        if not token:
            return {"error": "Failed to obtain access token."}, 401  # Handle token acquisition failure

        headers = {"Authorization": f"Bearer {token}"}

        # Step 1: Find the user by email
        user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user = user_response.json()

        user_id = user.get("id")
        if not user_id:
            return {"error": "User  not found."}, 404

        # Step 2: Get the application roles for the service principal
        service_principal_id = current_app.config['SERVICE_PRINCIPAL']
        roles_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_id}/appRoles"
        roles_response = requests.get(roles_url, headers=headers)
        roles_response.raise_for_status()
        roles = roles_response.json().get("value", [])

        sp_details_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_id}"
        sp_response = requests.get(sp_details_url, headers=headers)
        sp_response.raise_for_status()
        sp_details = sp_response.json()
        application_display_name = sp_details.get("displayName", "Unknown Application")

        # Step 3: Get role assignments for the user
        assignments_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/appRoleAssignments"
        assignments_response = requests.get(assignments_url, headers=headers)
        assignments_response.raise_for_status()
        assignments = assignments_response.json().get("value", [])

        # Step 4: Prepare the result
        result = []
        for assignment in assignments:
            role_id = assignment["appRoleId"]
            role_name = next((role["displayName"] for role in roles if role["id"] == role_id), "Unknown Role")
            assignment_date = assignment.get("createdDateTime", "N/A")
            result.append({
                "DisplayName": user.get("displayName"),
            
                "email": user.get("userPrincipalName"),
                "applicationDisplayName": application_display_name,  # Assuming this is the display name you want
                "roleName": role_name,
                "assignmentDate": assignment_date
            })

        return result, 200  # Return the data and status code

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error while fetching user roles: {req_err}")
        return {"error": "Failed to fetch data from Microsoft Graph API."}, 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}, 500