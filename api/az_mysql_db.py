import MySQLdb.cursors
from flask import session
import json
import uuid
from datetime import date
from datetime import datetime

from flask.helpers import total_seconds
from werkzeug.datastructures import ResponseCacheControl
from cloud_resources import calculate_invoice, creation_status, date_time_now


def account_exist(mysql, username, password):
    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()
    return True if account else False

def get_account(mysql, username, password):
    # Check if account exists using MySQL
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE username = %s AND password = %s', (username, password))
    account = cursor.fetchone()
    return account

def create_session(account):
    # Create session data, we can access this data in other routes
    session['loggedin'] = True
    session['id'] = account['id']
    session['username'] = account['username']

def get_account_info(mysql):
    # We need all the account info for the user so we can display it on the profile page
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM accounts WHERE id = %s', (session['id'],))
    account = cursor.fetchone()
    return account

def create_vm(
        mysql,
        subscription,
        resource_group,
        region,
        availability_zone,
        images,
        instance_azure_spot,
        sizes,
        authentication_type,
        username,
        password,
        ssh_public_key_source,
        key_pair_name,
        stored_keys,
        ssh_public_key,
        public_inbound_ports,
        http,
        https,
        ssh,
        name
    ):
    # create vm on table azureservers
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
    INSERT INTO azureservers (
        uid,
        name,
        account_id,
        subscription,
        resource_group,
        region,
        availability_zone,
        images,
        instance_azure_spot,
        sizes,
        authentication_type,
        username,
        password,
        ssh_public_key_source,
        key_pair_name,
        stored_keys,
        ssh_public_key,
        public_inbound_ports,
        http,
        https,
        ssh
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
    """
    uid = uuid.uuid4().hex
    cursor.execute(sql, (
        uid,
        name,
        session['id'],
        subscription,
        resource_group,
        region,
        availability_zone,
        images,
        instance_azure_spot,
        sizes,
        authentication_type,
        username,
        password,
        ssh_public_key_source,
        key_pair_name,
        stored_keys,
        ssh_public_key,
        public_inbound_ports,
        http,
        https,
        ssh
    ))
    mysql.connection.commit()
    date, time = date_time_now()
    status = "on"
    uptime = "0"
    service = "azure_virtual_machine"
    insert_log(mysql, uid, service, date, time, uptime, status)
    create_invoice(mysql, "Azure virtual machine", uid)
    return creation_status()
    
def insert_log(
        mysql,
        azureservers_id,
        service,
        creation_date,
        creation_time,
        uptime,
        status
    ):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
    INSERT INTO azurelogs (
        azureservers_id,
        account_id,
        service,
        creation_date,
        creation_time,
        uptime,
        status
    )
    VALUES (%s,%s,%s,%s,%s,%s,%s)
    """
    cursor.execute(sql, (
        azureservers_id,
        session['id'],
        service,
        creation_date,
        creation_time,
        uptime,
        status
    ))
    mysql.connection.commit()


def create_invoice(mysql, service, uid):
    total = "0"
    # creates invoice
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
    INSERT INTO invoices (
        service,
        uid,
        total,
        account_id
    )
    VALUES (%s,%s,%s,%s)
    """
    cursor.execute(sql, (service, uid, total, session['id']))
    mysql.connection.commit()

def update_invoice_total(mysql, uid, total_price):
   # updates total price
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
    UPDATE invoices
    SET total = %s
    WHERE uid = %s
    """
    cursor.execute(sql, (total_price, uid))
    mysql.connection.commit()

def get_invoices(mysql):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT service, uid, total FROM invoices')
    response = {}
    invoices = cursor.fetchall()
    for invoice in invoices:
        response[invoice["uid"]] = {
            "service": invoice["service"],
            "total": invoice["total"]
        }
    return response



def update_invoices(mysql):
    uids = get_uids(mysql)
    server_sizes_and_prices = json.loads(get_server_sizes_and_prices(mysql))
    for uid in uids:
        server_size = get_server(mysql, uid)["sizes"]
        for server_size_and_price in server_sizes_and_prices:
           if server_size_and_price["size"] == server_size:
                price = float(server_size_and_price["price"])
                server_uptime = float(uptime(mysql, uid))
                total_price = calculate_invoice(price, server_uptime)
                update_invoice_total(mysql, uid, total_price)
    return get_invoices(mysql)

def update_azurelogs(mysql):
    uids = get_uids(mysql)
    for uid in uids:
        uptime(mysql, uid)

def get_uids(mysql):
    # returns one uid
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT uid FROM azureservers WHERE account_id = %s', (session['id'],))
    response = []
    uids = cursor.fetchall()
    for uid in uids:
        response.append(uid["uid"])
    return response

def get_server_sizes_and_prices(mysql): # change function name
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT size, price FROM azureserversizes')
    return json.dumps(cursor.fetchall())

def uptime(mysql, uid):
    # get date and time
    datetime_query = get_date_time(mysql, uid)
    today = datetime.now()
    time_delta = today - datetime_query
    total_seconds = time_delta.total_seconds()
    minutes = str(total_seconds/60)

    # updates uptime
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    sql = """
    UPDATE azurelogs
    SET uptime = %s
    WHERE azureservers_id = %s
    """
    cursor.execute(sql, (minutes, uid))
    mysql.connection.commit()
    return minutes

def get_date_time(mysql, uid):
    #returns date and time from db and returns datetime object
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT creation_date, creation_time FROM azurelogs WHERE azureservers_id = %s', (uid,))
    query = cursor.fetchall()
    print(query)
    date, time = query[0]["creation_date"], query[0]["creation_time"]
    date_and_time = f"{date} {time}"
    return datetime.strptime(date_and_time, '%Y-%m-%d %H:%M:%S.%f')

def get_servers(mysql):
    # returns the list of currents servers for a user
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM azureservers WHERE account_id = %s', (session['id'],))
    servers = cursor.fetchall()
    response = []
    for i, server in enumerate(servers):
        response.append(
            {
            "name" : server["name"],
            "uid" : server["uid"]
            }
        )
    return json.dumps(response)

def get_server(mysql, uid):
    # return server for a user based on uid
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM azureservers WHERE uid = %s', (uid,))
    server = cursor.fetchone()
    response = {
        "uid" : uid,
        "name" : server["name"],
        "subscription": server["subscription"],
        "resource_group": server["resource_group"],
        "region": server["region"],
        "availability_zone": server["availability_zone"],
        "images": server["images"],
        "instance_azure_spot": server["instance_azure_spot"],
        "sizes": server["sizes"],
        "authentication_type": server["authentication_type"],
        "public_inbound_ports": [
            server["public_inbound_ports"],
            {
                "http": server["http"],
                "https": server["https"],
                "ssh": server["ssh"]
            }
        ]
    }
    return response

def get_server_size_info(mysql):
    # returns info of server sizes
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM azureserversizes')
    server_sizes = cursor.fetchall()
    for server_size in server_sizes:
        server_size.pop("id")
    return server_sizes

def get_server_available_data(mysql):
    subscriptions = [
        {f"foo_subscription_{i+1}": [f"resource_group_{j+1}" for j in range(3)]} for i in range(2)
    ]
    region = ["francecentral", "westus", "europe"]
    availability_zone = [
        "Aucune redondance",
        "Zone de disponibilité",
        "Group à haute disponibilité"
    ]
    images = [
        "Ubuntu Server 18.04 LTS - Gen2",
        "Ubuntu Server 20.04 LTS - Gen2",
        "Windows Server 2019 Datacenter - Gen2"
    ]
    instance_azure_spot = [True, False]
    sizes = get_server_size_info(mysql)
    authentication_type = {
        "SSH public": [
            "username",
            {
                "ssh_public_key_source": {
                    "Generate new key pair": "Key pair name",
                    "Use existing key stored in Azure": "Stored Keys",
                    "Use existing public key": "SSH public key"
                }
            }
        ],
        "Password": [
            "username",
            "password"
        ]
    }
    public_inbound_ports = [
        "None",
        {
        "Allow selected ports": {
            "Selected inbound ports": [
                "HTTP (80)",
                "HTTPS (443)",
                "SSH (22)"
            ]
        }
      }
    ]
    available_data = {
        "subscriptions": subscriptions,
        "regions": region,
        "availability_zone": availability_zone,
        "instance_azure_spot": instance_azure_spot,
        "images": images,
        "sizes": sizes,
        "authentication_type": authentication_type,
        "public_inbound_ports": public_inbound_ports
    }
    return available_data