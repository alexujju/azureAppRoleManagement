# app.py
from flask import Flask, redirect, render_template, request, session, url_for
from flask_session import Session
from auth_helper import log_in, complete_log_in, log_out, get_token_for_user, get_user
import app_config
import requests
from auth_helper import get_access_token
from roles_helper import fetch_app_roles, get_user_roles_with_names, get_user_roles_by_email, assign_roles_to_user, remove_user_roles
#from roles_helper import get_user_roles_with_names
from flask import jsonify

app = Flask(__name__)
app.config.from_object(app_config)
#app.config['SERVICE_PRINCIPAL'] = 'your_service_principal_id'
Session(app)

@app.route("/login")
def login():
    return render_template("login.html", **log_in())

@app.route(app_config.REDIRECT_PATH)
def auth_response():
    result = complete_log_in(request.args)
    if "error" in result:
        return render_template("auth_error.html", result=result)
    return redirect(url_for("index"))

@app.route("/logout")
def logout():
    return redirect(log_out(url_for("index", _external=True)))

@app.route("/")
def index():
    if not get_user():
        return redirect(url_for("login"))
    return render_template('index.html', user=get_user())

@app.route("/call_downstream_api")
def call_downstream_api():
    token = get_token_for_user()
    if "error" in token:
        return redirect(url_for("login"))
    api_result = requests.get(
        app_config.ENDPOINT,
        headers={'Authorization': 'Bearer ' + token['access_token']},
        timeout=30,
    ).json()
    return render_template('display.html', result=api_result)

@app.route("/roles", methods=["GET"])
def fetch_roles():
    try:
        roles = fetch_app_roles()  # Call the function to fetch roles
        print("Roles response:", roles)  # Debug output
        return jsonify(roles), 200  # Return roles as JSON
    except Exception as e:
        return jsonify({"error": str(e)}), 500  # Return error message in JSON format in case of failure
    

@app.route("/users_with_roles", methods=["GET"])
def user_roles():
    data, status_code = get_user_roles_with_names()
    return jsonify(data), status_code


@app.route("/user_roles", methods=["POST"])
def user_roles_by_email():
    data = request.get_json()
    email = data.get("email")


    if not email:
        return jsonify({"error": "Email parameter is required."}), 400

    data, status_code = get_user_roles_by_email(email)
    return jsonify(data), status_code


@app.route("/assign_roles", methods=["POST"])
def assign_roles():
    data = request.get_json()
    email = data.get("email")
    role_ids = data.get("role_ids")  # Expecting a list of role IDs

    if not email or not role_ids:
        return jsonify({"error": "Email and role IDs are required."}), 400

    response, status_code = assign_roles_to_user(email, role_ids)
    return jsonify(response), status_code

@app.route("/remove_roles", methods= ["DELETE"])
def remove_roles():
    data =  request.get_json()
    email =  data.get("email")
    role_ids = data.get("role_ids") #expecting a list role to get 
    if not email or not role_ids:
        return jsonify({"error": "Email and role IDs are required."}), 400
    
    response, status_code = remove_user_roles(email, role_ids)
    return jsonify(response), status_code


if __name__ == "__main__":
    app.run(debug=True)
