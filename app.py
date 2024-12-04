from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
from plaid.model.accounts_balance_get_request import AccountsBalanceGetRequest
from quickstart.quickstart.python.server import access_token, client

app = Flask(__name__)

# Configure Gemini AI
genai.configure(api_key="AIzaSyCFfbnibEYZFMo5E584oSdb4kohWaJx2S8")  # Replace with your Gemini API Key
model = genai.GenerativeModel("gemini-1.5-flash")

# Route to render the home page (popup.html)
@app.route('/')
def home():
    return render_template('popup.html')  # Ensure popup.html exists in a "templates" folder

# Route to analyze a purchase
@app.route('/analyze_purchase', methods=['POST'])
def analyze_purchase():
    try:
        # Get product data from frontend
        data = request.json
        product = data.get('product')
        if not product:
            return jsonify({"error": "Product information is missing"}), 400

        # Retrieve user's financial data using Plaid
        balance_request = AccountsBalanceGetRequest(access_token=access_token)
        balance_response = client.accounts_balance_get(balance_request)
        accounts = balance_response['accounts']

        # Aggregate account balances and prepare transaction data
        total_balance = sum(account.balances.available for account in accounts if account.balances.available)
        recent_transactions = [
            {"name": account.name, "balance": account.balances.available} for account in accounts
        ]

        # Prepare data for Gemini recommendation
        financial_summary = {
            "total_balance": total_balance,
            "recent_transactions": recent_transactions
        }

        # Generate recommendation using Gemini
        prompt = (
            f"I am considering buying {product}. My current financial situation includes a total "
            f"balance of ${total_balance:.2f} and the following recent transactions: {recent_transactions}. "
            "Should I proceed with this purchase? Provide a recommendation."
        )
        gem_response = model.generate_content(prompt)
        gem_result = gem_response.text.strip()

        # Return recommendation to frontend
        return jsonify({
            "product": product,
            "financial_summary": financial_summary,
            "recommendation": gem_result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    # Ensure the app runs on port 8000 as intended
    app.run(debug=True, host='127.0.0.1', port=8000)
