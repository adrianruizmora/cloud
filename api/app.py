from flask import Flask, request, session, redirect, url_for
import os

from flask.wrappers import Response
from werkzeug.wrappers import response
from flask_mysqldb import MySQL
import MySQLdb.cursors

from az_mysql_db import *
from cloud_resources import *

app = Flask(__name__)

# Change this to your secret key (can be anything, it's for extra protection)
app.secret_key = os.environ.get("APP_SECRET_KEY")

# Enter your database connection details below
app.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
app.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
app.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
app.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")


# Intialize MySQL
mysql = MySQL(app)

# Index
@app.route("/", methods=['GET'])
def index():
    return "index"

# Servers

@app.route("/api/iac/server", methods=['GET'])
def server():
    if 'loggedin' in session:
        return get_servers(mysql)

@app.route("/api/iac/server/create", methods=['GET', 'POST'])
def server_create():
    if 'loggedin' in session:
        if request.method == "GET":
            return get_server_available_data(mysql)
        if request.method == "POST":
            args =[
                "subscription",
                "resource_group",
                "region",
                "availability_zone",
                "images",
                "instance_azure_spot",
                "sizes",
                "authentication_type",
                "username",
                "password",
                "ssh_public_key_source",
                "key_pair_name",
                "stored_keys",
                "ssh_public_key",
                "public_inbound_ports",
                "http",
                "https",
                "ssh",
                "name"
            ]
            request_form = request.form
            form_inputs = args_in_form(args, request_form)
            if form_inputs:
                try:
                    return create_vm(
                        mysql,
                        request.form['subscription'],
                        request.form['resource_group'],
                        request.form['region'],
                        request.form['availability_zone'],
                        request.form['images'],
                        request.form['instance_azure_spot'],
                        request.form['sizes'],
                        request.form['authentication_type'],
                        request.form['username'],
                        request.form['password'],
                        request.form['ssh_public_key_source'],
                        request.form['key_pair_name'],
                        request.form['stored_keys'],
                        request.form['ssh_public_key'],
                        request.form['public_inbound_ports'],
                        request.form['http'],
                        request.form['https'],
                        request.form['ssh'],
                        request.form['name']
                    )
                except Exception:
                    return {"status": "error"}

    return redirect(url_for("index"))

@app.route("/api/iac/server/<uid>", methods=['GET', 'POST'])
def server_uid(uid):
    if 'loggedin' in session:
        return get_server(mysql, uid)
    return redirect(url_for("index"))
# IP

@app.route("/api/iac/ip", methods=['GET', 'POST'])
def ip():
    return "ip"

# Docker

@app.route("/api/iac/docker", methods=['GET'])
def docker():
    return "docker"

@app.route("/api/iac/docker/<uid>", methods=['GET', 'POST'])
def docker_uid():
    return "docker"

@app.route("/api/iac/docker/create", methods=['POST'])
def docker_create():
    return "docker"

# Factures

@app.route("/api/account/invoices", methods=['GET', 'POST'])
def invoice():
    return update_invoices(mysql)

# Profile

@app.route('/api/account/login', methods=['GET', 'POST'])
def login():
    # Output message if something goes wrong...
    msg = ''

    # Check if "username" and "password" POST requests exist (user submitted form)
    if request.method == 'POST' and 'username' in request.form and 'password' in request.form:
        # Create variables for easy access
        username = request.form['username']
        password = request.form['password']

        # If account exists in accounts table in out database
        if account_exist(mysql, username, password):
            account = get_account(mysql, username, password)
            create_session(account)
            # Return session
            response = {
                "loggedin": session["loggedin"]
            }
            return response
        else:
            # Account doesnt exist or username/password incorrect
            msg = 'Incorrect username/password!'
            return msg
    return redirect(url_for('index'))

@app.route('/api/account/logout')
def logout():
    # Remove session data, this will log the user out
   session.pop('loggedin', None)
   session.pop('id', None)
   session.pop('username', None)
   # Redirect to login page
   return redirect(url_for('index'))

@app.route("/api/account/profil", methods=['GET', 'POST'])
def profil():
    """
    GET: Return data about the current auth user.
    POST: update data for auth user.
    """
    # Check if user is loggedin
    if 'loggedin' in session:
        account = get_account_info(mysql)
        # Show the profile page with account info
        response = {
            "username": account["username"],
            "email": account["email"]
        }
        return response
    # User is not loggedin redirect to login page
    return redirect(url_for('index'))