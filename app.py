from flask import Flask,jsonify,request
from functools import wraps
import logic

app = Flask(__name__)

SECRET_API_KEY = "my-super-secret-key-123"

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if request.headers.get('X-API-Key') and request.headers.get('X-API-Key') == SECRET_API_KEY:
            return f(*args, **kwargs)
        else:
            return jsonify({"error": "Unauthorized - Missing or invalid API Key"}), 401
    return decorated_function

@app.route('/query', methods=['POST'])
@require_api_key
def handle_query():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    nl_query = data.get('query')

    if not nl_query:
        return jsonify({"error": "Missing 'query' field in request body"}), 400

    try:
        intent = logic.parse_query_intent(nl_query)
        if not intent["valid"]:
            return jsonify({"error": f"Query validation failed: {intent['reason']}", "details": intent["explanation_steps"]}), 400
        result = logic.execute_query(intent)
        if "error" in result:
             return jsonify(result), 500 

        return jsonify(result), 200

    except Exception as e:
        print(f"Unexpected error in /query: {e}") 
        return jsonify({"error": "An unexpected internal server error occurred."}), 500


@app.route('/explain', methods=['POST'])
@require_api_key
def handle_explain():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    nl_query = data.get('query')

    if not nl_query:
        return jsonify({"error": "Missing 'query' field in request body"}), 400

    try:
        intent = logic.parse_query_intent(nl_query)

        response = {
            "query": nl_query,
            "simulated_sql": intent.get("pseudo_sql", "Could not generate simulated SQL."),
            "parsing_steps": intent.get("explanation_steps", ["Error during parsing."]),
            "parsed_intent": {
                 "action": intent.get("action"),
                 "target_field": intent.get("target_field"),
                 "filters": intent.get("filters")
             },
            "is_understood": intent.get("valid", False),
             "validation_reason": intent.get("reason", "Parsing failed.")
        }
        return jsonify(response), 200

    except Exception as e:
        print(f"Unexpected error in /explain: {e}")
        return jsonify({"error": "An unexpected internal server error occurred."}), 500


@app.route('/validate', methods=['POST'])
@require_api_key
def handle_validate():
    if not request.is_json:
        return jsonify({"error": "Request must be JSON"}), 400

    data = request.get_json()
    nl_query = data.get('query')

    if not nl_query:
        return jsonify({"error": "Missing 'query' field in request body"}), 400

    try:
        intent = logic.parse_query_intent(nl_query)

        response = {
            "query": nl_query,
            "is_valid_for_processing": intent.get("valid", False),
            "reason": intent.get("reason", "Could not parse query or parsing failed.")
        }
        status_code = 200 if intent.get("valid") else 400 
        return jsonify(response), status_code 

    except Exception as e:
        print(f"Unexpected error in /validate: {e}")
        return jsonify({"error": "An unexpected internal server error occurred."}), 500

@app.route('/')
def index():
    return jsonify({"message":"AI Query Simulator API is running!!"})

if __name__ == '__main__':
    app.run(debug=True,port=5001)