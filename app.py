import time
from datetime import datetime, timedelta

from flask import Flask, jsonify, request, render_template
import google.generativeai as genai
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest

from quickstart.python.server import client

app = Flask(__name__)

genai.configure(api_key="AIzaSyCFfbnibEYZFMo5E584oSdb4kohWaJx2S8")
model = genai.GenerativeModel("gemini-1.5-flash")

access_token = None


@app.route('/')
def home():
    return render_template("popup.html")


@app.route('/popup', methods=['GET'])
def popup_advisor():
    try:
        text_result = get_balance_and_recommendation()
        return render_template('popup_advisor.html', text_result=text_result)
    except Exception as e:
        print(f"Error in popup route: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/create_link_token', methods=['POST'])
def create_link_token():
    try:
        request = LinkTokenCreateRequest(
            user=LinkTokenCreateRequestUser(
                client_user_id=str(time.time())
            ),
            client_name="Plaid Quickstart",
            products=[Products("auth")],
            country_codes=[CountryCode("US")],
            language="en",
        )
        response = client.link_token_create(request)
        return jsonify(response.to_dict())
    except Exception as e:
        print(f"Error in create_link_token: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/transactions', methods=['POST'])
def get_transactions():
    global access_token
    access_token = request.json.get('access_token')
    if not access_token:
        return jsonify({'error': 'Access token is missing'}), 400

    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        transactions_request = TransactionsGetRequest(
            access_token=access_token,
            start_date=start_date.strftime('%Y-%m-%d'),
            end_date=end_date.strftime('%Y-%m-%d')
        )

        response = client.transactions_get(transactions_request)
        transactions = response['transactions']

        transaction_dict = {
            transaction['transaction_id']: {
                'object': transaction['name'],
                'price': transaction['amount']
            }
            for transaction in transactions
        }

        return jsonify(transaction_dict)
    except Exception as e:
        print(f"Error in get_transactions: {str(e)}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/balance', methods=['POST', 'GET'])
def get_balance_and_recommendation():
    global access_token

    if request.method == 'POST':
        access_token = request.json.get('access_token')
        product_title = request.json.get('product_name', 'Unknown Product')  # Get product title from frontend
        if not access_token:
            return jsonify({'error': 'Access token is missing'}), 400

    try:
        balance_request = AccountsBalanceGetRequest(access_token=access_token)
        response = client.accounts_balance_get(balance_request)
        accounts = response['accounts']

        transactions_response = get_transactions()
        if isinstance(transactions_response, dict):
            transactions = transactions_response
        else:
            transactions = transactions_response.get_json()

        gen_response = model.generate_content(
            f"Recommend me the product '{product_title}' based on my current transactions: {transactions} and current bank balance: {accounts}"
        )
        return jsonify({'recommendation': gen_response.text})
    except Exception as e:
        print(f"Error in get_balance_and_recommendation: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
