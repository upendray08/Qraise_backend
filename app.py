from flask import Flask, render_template, request, jsonify, session
import mysql.connector
from flask_cors import CORS
from flask_session import Session
import os
import razorpay
from werkzeug.utils import secure_filename


# Generate a random secret key
secret_key = os.urandom(24).hex()
value_cache = {}


app = Flask(__name__)
CORS(app)

app.secret_key = secret_key

app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

db = mysql.connector.connect(
    host="localhost",
    user="root",
    password="Yupen@240800",
    database="qraise",
    port=3306
)

cursor = db.cursor()


@app.route('/')
def hello():
    if 'user_id' in value_cache:
        value = value_cache['user_id']
        print(value)
        return jsonify({'user_id': value})
    return "Hello, World!"


@app.route('/apiuserid', methods=['GET'])
def apiuserid():
    userId = ""
    if 'user_id' in value_cache:
        userId = value_cache['user_id']
        print(userId)

    return jsonify({'user_id': userId})


@app.route('/submit_campaign', methods=['POST'])
def submit_campaign():
    try:
        if request.method == 'POST':
            data = request.json

            campaign_name = data['campaign_name']
            short_desc = data.get('short_desc')
            description = data['description']
            target_amt = data['target_amt']
            category_id = data['category_id']
            deadline = data['deadline']
            media_path = str(data.get('media_path'))
            raised_amt = data.get("raised_amt")
            print(media_path)
            if 'user_id' not in value_cache:
                user_id = str(None)
            user_id = str(value_cache['user_id'])
            print(user_id)
            query = 'INSERT INTO campaigns (campaign_name, short_desc, description, target_amt, category_id, deadline, media_path, user_id,raised_amt) VALUES (%s, %s, %s, %s, %s, %s, %s, %s,%s)'
            print(query)
            values = (campaign_name, short_desc, description,
                      target_amt, category_id, deadline, media_path, user_id, raised_amt)
            print(values)
            cursor.execute(query, values)
            print(data)
            db.commit()

            return jsonify({'message': 'Campaign submitted successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/editcampaign', methods=['PUT'])
def edit_campaign():
    res = request.get_json()
    campaigns_id = res.get('campaignIdToEdit')
    campaignName = res.get('camp_Name')
    campaignDesc = res.get('camp_Desc')
    campaignTargetAmount = res.get('camp_amt')
    campaignDeadline = res.get('camp_deadline')
    campaignShortDesc = res.get('camp_shortdesc')
    cursor.execute(
        'UPDATE campaigns SET campaign_name = %s, description = %s, target_amt = %s, short_desc = %s, deadline = %s WHERE id = %s',
        (campaignName, campaignDesc, campaignTargetAmount,
         campaignShortDesc, campaignDeadline, campaigns_id)
    )
    db.commit()
    return jsonify("updated")


@app.route('/delete_campaign/<int:campaign_id>', methods=['DELETE'])
def delete_campaign(campaign_id):
    try:

        print(campaign_id)
        cursor.execute("DELETE FROM campaigns WHERE id = %s", (campaign_id,))
        # Commit the changes to the database
        db.commit()
        return jsonify({'message': 'Campaign deleted successfully'})

    except Exception as e:
        print(e)
        return jsonify({'error': 'An error occurred while deleting the campaign'})


@app.route('/campaignDetails', methods=['POST'])
def campaign_details():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Yupen@240800",
            database="qraise",
            port=3306
        )
        cursor = db.cursor()
        res = request.get_json()
        campaigns_id = int(res.get('campaignId'))
        print(campaigns_id)
        cursor.execute(
            'SELECT id, campaign_name, short_desc, description, target_amt, category_id, deadline, media_path,raised_amt FROM campaigns where id = %s', (campaigns_id,))
        data = cursor.fetchone()
        print(data)
        # Convert data to a tuple of dictionarie
        campaign_dict = {
            'id': str(data[0]),
            'campaign_name': data[1],
            'short_desc': data[2],
            'description': data[3],
            'target_amt': str(data[4]),
            'category_id': data[5],
            'deadline': str(data[6]),
            'media_path': data[7],
            'raised_amt': data[8]
        }
        print(campaign_dict)
        cursor.close()
        return jsonify(campaign_dict)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/get_campaigns', methods=['GET'])
def get_campaigns():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Yupen@240800",
            database="qraise",
            port=3306
        )
        cursor = db.cursor()
        cursor.execute(
            'SELECT id, campaign_name, short_desc, description, target_amt, category_id, deadline, media_path, raised_amt FROM campaigns')
        data = cursor.fetchall()

        # Convert data to a list of dictionaries
        campaigns = [{'id': campaign[0], 'campaign_name': campaign[1], 'short_desc': campaign[2],
                      'description': campaign[3], 'target_amt': str(campaign[4]), 'category_id': campaign[5],
                      'deadline': str(campaign[6]), 'media_path': campaign[7], 'raised_amt':campaign[8]} for campaign in data]
        cursor.close()
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/get_yourcampaign', methods=['GET'])
def get_yourcampaign():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",
            password="Yupen@240800",
            database="qraise",
            port=3306
        )
        cursor = db.cursor()
        if 'user_id' not in value_cache:
            user_id = None
        user_id = value_cache['user_id']
        cursor.execute(
            'SELECT id, campaign_name, short_desc, description, target_amt, category_id, deadline, media_path,raised_amt FROM campaigns where user_id =%s', (user_id,))
        data = cursor.fetchall()

        # Convert data to a list of dictionaries
        campaigns = [{'id': campaign[0], 'campaign_name': campaign[1], 'short_desc': campaign[2],
                      'description': campaign[3], 'target_amt': str(campaign[4]), 'category_id': campaign[5],
                      'deadline': str(campaign[6]), 'media_path': campaign[7], 'raised_amt':campaign[8]} for campaign in data]
        cursor.close()
        return jsonify(campaigns)
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/update_campaign/<int:id>', methods=['PUT'])
def update_campaign(id):
    try:
        if request.method == 'PUT':
            data = request.json
            campaign_name = data.get('campaign_name')
            short_desc = data.get('short_desc')
            description = data.get('description')
            target_amt = data.get('target_amt')
            category_id = data.get('category_id')
            deadline = data.get('deadline')
            media_path = data.get('media_path')

            cursor.execute('UPDATE campaigns SET campaign_name = %s, short_desc = %s, description = %s, target_amt = %s, category_id = %s, deadline = %s, media_path = %s WHERE id = %s',
                           (campaign_name, short_desc, description, target_amt, category_id, deadline, media_path, id))
            db.commit()
            cursor.close()
            return jsonify({'message': 'Campaign updated successfully'})
    except Exception as e:
        return jsonify({'error': str(e)})


@app.route('/register', methods=['POST'])
def register():
    res = request.get_json()
    email = res.get('email')
    name = res.get('name')
    password = res.get('password')
    cpassword = res.get('cpassword')
    phone = res.get('phone')
    ale = password == cpassword
    if ale:
        if name and email and password:
            # Check if the user already exists
            query = "SELECT email FROM users WHERE email = %s"
            cursor.execute(query, (email,))
            user_email = cursor.fetchone()
            if user_email:
                return jsonify({"resp": "User already exists", "status": 0})

            # Insert the user into the database and capture the user_id
            insert_query = "INSERT INTO users (email, name, password, phone) VALUES (%s, %s, %s, %s)"
            values = (email, name, password, phone)
            cursor.execute(insert_query, values)
            db.commit()

            # Capture the user_id of the newly registered user
            user_id = cursor.lastrowid
         #    print(user_id)

            cursor.close()
            db.close()

            return jsonify({"resp": "User created successfully", "status": 1, "user_id": user_id})
        else:
            return jsonify({"resp": "Name, email, and password are required", "status": 2})
    else:
        return jsonify({"resp": "Password and confirm password do not match", "status": 3})


@app.route('/get_session_data', methods=['GET'])
def get_session_data():
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    email = session.get('email')
    password = session.get('password')
    print(user_id)
    return jsonify({"user_id": user_id, "user_name": user_name, "email": email, "password": password})


@app.route('/get_profile', methods=['GET'])
def get_profile():
    try:
        if 'user_id' in value_cache:
            user_id = value_cache['user_id']
        cursor.execute("SELECT * FROM users WHERE id = %s", (user_id,))
        data = cursor.fetchone()
        print(data)

        if data:
            profile = {
                'user_id': data[0],
                'email': data[1],
                'name': data[2],
                'password': data[3],
                'phone': data[4]
            }
            return jsonify(profile)
        else:
            return jsonify({'message': 'Profile not found'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/updated_profile', methods=['POST'])
def update_profile():
    try:
        # Get data from the request
        data = request.get_json()
        user_id = data['user_id']
        username = data['username']
        phone = data['phone']
        email = data['email']

        # Update the user's profile in the database
        cursor.execute("UPDATE users SET name = %s, phone = %s, email = %s WHERE id = %s",
                       (username, phone, email, user_id))
        db.commit()
        return jsonify({"message": "Profile updated successfully"})
    except Exception as e:
        return jsonify({"error": str(e)})


var_email = None


@app.route('/login', methods=['POST'])
def login():
    res = request.get_json()
    email = res.get('email')
    global var_email
    var_email = email
    password = res.get('password')
    query = "SELECT id,name,password,email FROM users WHERE email = %s"
    cursor.execute(query, (email,))
    user_data = cursor.fetchone()

    if user_data:
        db_password = user_data[2]
        if db_password == password:
            # Store user information in the session
            session['user_id'] = user_data[0]
            # print(session['user_id'])
            session['user_name'] = user_data[1]
            # print(session['user_name'])
            session['password'] = user_data[2]
            session['email'] = user_data[3]
            value_cache['user_id'] = user_data[0]
            return jsonify({"resp": "Login successfully", "status": 1, "udata": user_data})
        else:
            return jsonify({"resp": "Incorrect Password", "status": 2})
    else:
        return jsonify({"resp": "User does not exist", "status": 0})


@app.route('/forgot', methods=['POST'])
def forgot():
    res = request.get_json()
    email = res.get('email')
    cupassword = res.get('cupassword')
    password = res.get('password')
    repassword = res.get('repassword')
    print(res)
    if password == repassword:
        query = "SELECT email,password FROM users where email=%s"
        cursor.execute(query, (email,))
        data = cursor.fetchall()
        # print(len(data))
        if len(data) > 0:
            em, ps = data[0]
            if ps == cupassword:
                query = "UPDATE users SET password = %s WHERE email = %s"
                cursor.execute(query, (password, em))
                db.commit()
                return jsonify({"resp": "update pass", "status": 1})
            return jsonify({"resp": "entered wrong current password", "status": 0})
        return jsonify({"resp": "email doesn't exist", "status": 2})
    return jsonify({"resp": "password and confirm password doesn't match", "status": 3})


client = razorpay.Client(
    auth=("rzp_test_aZfDkycbpZZrus", "KQVk7m8dSrBhrSgpcJ7R8FJy"))


@app.route('/create_order', methods=["POST"])
def create_order():
    amount = request.form.get("amount")
    if amount:
        try:
            amount_in_paise = int(float(amount) * 100)
            data = {"amount": amount_in_paise,
                    "currency": "INR", "receipt": "order_rcptid_11"}
            payment = client.order.create(data=data)
            return jsonify({"order_id": payment["id"], "amount": amount_in_paise})
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"error": "Amount not provided"}), 400


@app.route('/success', methods=['POST'])
def payment_success():
    data = request.json
    print("Payment Details:", data)
    db_conn = mysql.connector.connect(
        host="localhost",
        user="root",
        password="Yupen@240800",
        database="qraise",
        port=3306)
    cursor = db_conn.cursor()
    if (data['payment_id']):
        try:
            query = (
                "INSERT INTO payment (name, campaign, date, email, phone, amount, payment_id) "
                "VALUES (%s, %s, %s, %s, %s, %s, %s)"
            )
            query1 = "select raised_amt from campaigns where campaign_name= %s"
            cursor.execute(query1, (data['campaign'],))
            totaldata = cursor.fetchall()
            new_amount = int(data['amount'])
            totaldata1 = int(totaldata[0][0]) + new_amount
            print(totaldata1)
            print(totaldata)
            query2 = "UPDATE campaigns SET raised_amt =%s WHERE campaign_name = %s"
            cursor.execute(query2, (str(totaldata1), data['campaign']))
            values = (
                data['name'],
                data['campaign'],
                data['date'],
                data['email'],
                data['phone'],
                data['amount'],
                data['payment_id'],
            )
            cursor.execute(query, values)
            db_conn.commit()

            return jsonify({'message': 'Payment data stored successfully'}), 200
        except mysql.connector.Error as err:

            db_conn.rollback()
            print("Something went wrong: {}".format(err))
            return jsonify({'error': 'Failed to store payment data'}), 500
        finally:
            cursor.close()
            db_conn.close()

    return jsonify(success=True, message="Payment recorded successfully"), 200


@app.route('/get-payment-data')
def get_payment_data():
    connection = mysql.connector.connect(
        host='localhost', database='qraise', user='root', password='Yupen@240800')
    cursor = connection.cursor()
    # cursor.execute("SELECT date, campaign, amount FROM payment")
    global var_email
    cursor.execute(
        "SELECT date, campaign, amount FROM payment WHERE email = %s", (var_email,))

    payment_data = cursor.fetchall()
    payments_list = []
    for payment in payment_data:
        payments_list.append({
            'date': payment[0],
            'campaign': payment[1],
            'amount': payment[2]
        })
    cursor.close()
    connection.close()
    return jsonify(payments_list)


@app.route('/camp', methods=['GET'])
def get_campaign_names():
    try:
        userId = ""
        if 'user_id' in value_cache:
            userId = value_cache['user_id']
        connection = mysql.connector.connect(
            host='localhost',
            database='qraise',
            user='root',
            password='Yupen@240800'
        )
        cursor = connection.cursor()
        cursor.execute("SELECT campaign_name FROM campaigns")
        campaign_data = cursor.fetchall()

        campaigns_list = [campaign[0] for campaign in campaign_data]

    except mysql.connector.Error as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return jsonify(campaigns_list)


@app.route('/total', methods=['GET'])
def get_campaign_donations():
    try:

        connection = mysql.connector.connect(
            host='localhost',
            database='qraise',
            user='root',
            password='Yupen@240800'
        )
        cursor = connection.cursor(dictionary=True)
        # sql_query = """
        # SELECT campaign, SUM(amount) AS total
        # FROM payment
        # GROUP BY campaign
        # """
        global var_email
        sql_query = """
        SELECT campaign, SUM(amount) AS total
        FROM payment
        WHERE email = var_email
        GROUP BY campaign
        """
        cursor.execute(sql_query)
        result = cursor.fetchall()
        donations_list = [{'campaign': row['campaign'],
                           'amount': row['total']} for row in result]
    except e as e:
        return jsonify({"error": str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
    return jsonify(donations_list)


if __name__ == '__main__':
    app.run(debug=True)
