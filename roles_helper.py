import requests
from flask import current_app
from auth_helper import get_access_token  # Import your token acquisition function
#import jsonify
import logging
from logging_config import logger

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

        #preparing the reuslt for the assigned role Ids and display name

        assigned_roles = []  # Store assigned roles with IDs and display names
        assigned_role_ids = []  # To filter available roles later
        for assignment in assignments:
            role_id = assignment["appRoleId"]
            assigned_role_ids.append(role_id)
            # Get the role name
            role_name = next((role["displayName"] for role in roles if role["id"] == role_id), "Unknown Role")
            assignment_date = assignment.get("createdDateTime", "N/A")
            if assignment_date != "N/A":
                assignment_date = assignment_date.replace('T', ' ')[:-1]  # Convert to "YYYY-MM-DD HH:MM:SS"
            
            assigned_roles.append({
                "id": role_id,
                "DisplayName": user.get("displayName"),
                "email": user.get("userPrincipalName"),
                "displayName": role_name,
                "assignmentDate": assignment_date

            })

        
        # Prepare the list of available roles
        available_roles = []
        for role in roles:
            role_display_name = role["displayName"]
            role_id = role["id"]
            available_roles.append({
                "id": role_id,
                "displayName": role_display_name
            })

        return {
            "assignedRoles": assigned_roles,  # Now includes IDs and display names
            "availableRoles": available_roles,
            "displayName": user.get("displayName"),
            "email": user.get("userPrincipalName"),

        }, 200  # Return the data and status code

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error while fetching user roles: {req_err}")
        return {"error": "Failed to fetch data from Microsoft Graph API."}, 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}, 500

def assign_roles_to_user(email, role_ids):
    try:
        
        token = get_access_token()
        if not token:
            return {"error": "Failed to obtain access token."}, 401  # Handle token acquisition failure

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 1: Find the user by email
        user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user = user_response.json()

        user_id = user.get("id")
        if not user_id:
            return {"error": "User not found."}, 404

        # Step 2: Assign roles
        assigned_role_ids = []  # To track successful assignments
        for role_id in role_ids:
            assignment_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/appRoleAssignments"
            assignment_data = {
                "principalId": user_id,
                "resourceId": current_app.config['SERVICE_PRINCIPAL'],  # Service principal ID
                "appRoleId": role_id  # Role ID to assign
            }

            # Make the request to assign the role
            assignment_response = requests.post(assignment_url, headers=headers, json=assignment_data)
            if assignment_response.status_code == 201:
                assigned_role_ids.append(role_id)  # Keep track of successfully assigned roles
            #logger.info(f"Attempting to assign role {assigned_role_ids} to user {user_id}")
        return {"message": f"Successfully assigned roles: {', '.join(assigned_role_ids)}"}, 201

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error while assigning roles: {req_err}")
        #logger.info(f"Successfully assigned role {assigned_role_ids} to user {user_id}")
        return {"error": "Failed to assign roles via Microsoft Graph API."}, 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}, 500


def remove_user_roles(email, role_ids):
    try:
        token = get_access_token()
        if not token:
            return {"error": "Failed to obtain access token."}, 401  # Handle token acquisition failure

        headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

        # Step 1: Find the user by email
        user_url = f"https://graph.microsoft.com/v1.0/users/{email}"
        user_response = requests.get(user_url, headers=headers)
        user_response.raise_for_status()
        user = user_response.json()
        
        user_id = user.get("id")
        if not user_id:
            return {"error": "User not found."}, 404

        service_principal_id = current_app.config['SERVICE_PRINCIPAL']  # Service principal ID from config
        removed_role_ids = []

        # Step 2: Get all assigned roles for the user in this service principal
        assigned_roles_url = f"https://graph.microsoft.com/v1.0/users/{user_id}/appRoleAssignments"
        assigned_roles_response = requests.get(assigned_roles_url, headers=headers)
        assigned_roles_response.raise_for_status()
        assigned_roles = assigned_roles_response.json().get("value", [])

        # Step 3: Identify and delete the specific role assignments
        for role in assigned_roles:
            if role.get("appRoleId") in role_ids and role.get("resourceId") == service_principal_id:
                app_role_assignment_id = role.get("id")
                
                # Construct the DELETE URL with the specific appRoleAssignment ID
                delete_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{service_principal_id}/appRoleAssignedTo/{app_role_assignment_id}"
                delete_response = requests.delete(delete_url, headers=headers)
                
                if delete_response.status_code == 204:
                    removed_role_ids.append(role.get("appRoleId"))

        if removed_role_ids:
            return {"message": f"Successfully removed roles: {', '.join(removed_role_ids)}"}, 200
        else:
            return {"message": "No roles were removed."}, 200

    except requests.exceptions.RequestException as req_err:
        logging.error(f"Request error while removing roles: {req_err}")
        return {"error": "Failed to remove roles via Microsoft Graph API."}, 500
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")
        return {"error": str(e)}, 500

    #     # Step 4: Prepare the result
    #     result = []
    #     for assignment in assignments:
    #         role_id = assignment["appRoleId"]
    #         role_name = next((role["displayName"] for role in roles if role["id"] == role_id), "Unknown Role")
    #         assignment_date = assignment.get("createdDateTime", "N/A")
    #         result.append({
    #             "DisplayName": user.get("displayName"),
            
    #             "email": user.get("userPrincipalName"),
    #             "applicationDisplayName": application_display_name,  # Assuming this is the display name you want
    #             "roleName": role_name,
    #             "assignmentDate": assignment_date
    #         })

    #     return result, 200  # Return the data and status code

    # except requests.exceptions.RequestException as req_err:
    #     logging.error(f"Request error while fetching user roles: {req_err}")
    #     return {"error": "Failed to fetch data from Microsoft Graph API."}, 500
    # except Exception as e:
    #     logging.error(f"An unexpected error occurred: {e}")
    #     return {"error": str(e)}, 500