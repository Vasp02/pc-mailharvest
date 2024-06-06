from flask import Flask, request, jsonify, Response
from flask_cors import CORS

import utils.dbutils
from controllers import auth_controller
from controllers import scrape_controller
from controllers import download_controller
import re
from entity.criteria import Criteria
import threading

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    return 'Hello, World!'

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data['email']
        password = data['password']

        jwt = auth_controller.login_user(email, password)
        if jwt:
            return jsonify({"message": "Login successful", "token": jwt}), 200
        else:
            return jsonify({"error": "Invalid credentials"}), 401
    except KeyError:
        return jsonify({"error": "Missing email or password"}), 400
    except Exception as e:
        print(e)
        return jsonify({"error": "Failed to process request. Please check credentials or try again later."}), 500

@app.route('/api/scrape', methods=['POST'])
def scrape():
    scrape_criteria = request.get_json()
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header) #regex
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                criteria = Criteria(**scrape_criteria)
                print(token)
                criteria.print_details()
                email, password = auth_controller.extract_email_and_password_from_jwt(token)
                emails = scrape_controller.scrape(email,password,criteria)
                user_email = auth_controller.validate_jwt(token).get('payload').get('email')
                scrape_controller.save_emails_to_db(emails,user_email)

    return jsonify({'emails' : emails}), 200

@app.route('/api/download/csv', methods=['GET'])
def download_csv():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header)  # regex
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                user_email = auth_controller.validate_jwt(token).get('payload').get('email')
                csv = download_controller.get_user_csv(user_email)

    response = Response(csv, mimetype='text/csv')
    response.headers.set('Content-Disposition', 'attachment', filename='user_data.csv')
    return response

@app.route('/api/uploadfilter' , methods=['POST'])
def upload_filter():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header)
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                email, password = auth_controller.extract_email_and_password_from_jwt(token)
                scrape_criteria = request.get_json()
                criteria = Criteria(**scrape_criteria)

                if not utils.dbutils.does_account_filters_table_exist():
                    utils.dbutils.create_account_filters_table()
                if not utils.dbutils.does_filter_scrapes_table_exist():
                    utils.dbutils.create_filter_scrapes_table()
                utils.dbutils.insert_new_account_filter(email, password, criteria)

                return jsonify({"status": "success", "message": "Filter uploaded successfully"}), 200
            else:
                return jsonify({"status": "error", "message": "Invalid token"}), 401
    return jsonify({"status": "error", "message": "Authorization header missing"}), 400


@app.route('/api/getuserfilters' , methods=['GET'])
def get_user_filter():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header)
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                email, password = auth_controller.extract_email_and_password_from_jwt(token)
                filters = utils.dbutils.get_all_filters_for_account(email)
                return jsonify({"status": "success", "filters": filters}), 200


@app.route('/api/deletefilterbyid', methods=['POST'])
def delete_user_filter():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header)
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                email, _ = auth_controller.extract_email_and_password_from_jwt(token)
                filter_id = request.get_json().get('filter_id')
                if filter_id is None:
                    return jsonify({'status': 'failure', 'message': 'filter_id not provided'}), 400

                if utils.dbutils.get_filter_id_owner(filter_id) == email:
                    utils.dbutils.delete_account_filter_by_id(filter_id)
                    return jsonify({'status': 'success', 'message': 'Filter deleted successfully'}), 200
                else:
                    return jsonify({'status': 'failure', 'message': 'Unauthorized'}), 403
            else:
                return jsonify({'status': 'failure', 'message': 'Invalid token'}), 401
    return jsonify({'status': 'failure', 'message': 'Authorization header missing'}), 401

@app.route('/api/getfilterscrapesbyid', methods=['POST'])
def get_filter_scrapes_by_id():
    auth_header = request.headers.get('Authorization')
    if auth_header:
        match = re.match(r'^Bearer\s+(.*)$', auth_header)
        if match:
            token = match.group(1)
            print("Token:", token)
            token_status = auth_controller.validate_jwt(token)
            if token_status.get('status') == 'success':
                email, _ = auth_controller.extract_email_and_password_from_jwt(token)
                filter_id = request.get_json().get('filter_id')
                if filter_id is None:
                    return jsonify({'status': 'failure', 'message': 'filter_id not provided'}), 400

                if utils.dbutils.get_filter_id_owner(filter_id) == email:
                    scrapes = utils.dbutils.get_scrapes_of_filter_id(filter_id)
                    return jsonify({'status': 'success', 'scrapes': scrapes}), 200
                else:
                    return jsonify({'status': 'failure', 'message': 'Unauthorized access'}), 403
            else:
                return jsonify({'status': 'failure', 'message': 'Invalid token'}), 401
    return jsonify({'status': 'failure', 'message': 'Authorization header not found'}), 401



if __name__ == '__main__':
    monitor_thread = threading.Thread(target=scrape_controller.monitor)
    monitor_thread.daemon = True
    monitor_thread.start()
    app.run(debug=True)