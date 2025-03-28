mock_data_db = [
    {"order_id": 1, "product": "Laptop", "category": "Electronics", "region": "North", "sales": 1200, "quantity": 1, "month": "Jan"},
    {"order_id": 2, "product": "Keyboard", "category": "Accessories", "region": "South", "sales": 75, "quantity": 3, "month": "Jan"},
    {"order_id": 3, "product": "Laptop", "category": "Electronics", "region": "North", "sales": 1350, "quantity": 1, "month": "Feb"},
    {"order_id": 4, "product": "Monitor", "category": "Electronics", "region": "West", "sales": 300, "quantity": 2, "month": "Feb"},
    {"order_id": 5, "product": "Keyboard", "category": "Accessories", "region": "North", "sales": 80, "quantity": 2, "month": "Mar"},
    {"order_id": 6, "product": "Mouse", "category": "Accessories", "region": "South", "sales": 25, "quantity": 5, "month": "Mar"},
    {"order_id": 7, "product": "Webcam", "category": "Accessories", "region": "West", "sales": 50, "quantity": 1, "month": "Jan"},
    {"order_id": 8, "product": "Monitor", "category": "Electronics", "region": "North", "sales": 320, "quantity": 1, "month": "Mar"},
]

KEYWORDS = {
    "actions": ["total", "sum", "count", "list", "show", "average", "avg"],
    "fields": ["sales", "quantity", "order", "orders"],
    "entities": ["product", "category", "region", "month"],
    "products": ["laptop", "keyboard", "monitor", "mouse", "webcam"],
    "categories": ["electronics", "accessories"],
    "regions": ["north", "south", "west", "east"], 
    "months": ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"]
}

def parse_query_intent(nl_query):
    """
    Very basic keyword spotting to understand the query intent.
    Returns a dictionary with parsed information or an error.
    """
    query = nl_query.lower()
    intent = {
        "action": "list", 
        "target_field": None, 
        "filters": {}, 
        "valid": True,
        "reason": "Query parsed successfully.",
        "pseudo_sql": "SELECT * FROM sales", 
        "explanation_steps": ["Starting query analysis."]
    }
    words = query.split()

    action_found = None
    for word in words:
        if word in KEYWORDS["actions"]:
            action_found = word
            intent["explanation_steps"].append(f"Identified action keyword: '{word}'.")
            break 

    if action_found in ["total", "sum"]:
        intent["action"] = "sum"
    elif action_found == "count":
        intent["action"] = "count"
    elif action_found in ["average", "avg"]:
         intent["action"] = "average"
    elif action_found in ["list", "show"]:
         intent["action"] = "list"

    if intent["action"] in ["sum", "average"]:
        for word in words:
            if word in KEYWORDS["fields"]:
                intent["target_field"] = word
                intent["explanation_steps"].append(f"Identified target field for aggregation: '{word}'.")
                break 
        if not intent["target_field"]:
             intent["valid"] = False
             intent["reason"] = f"Action '{intent['action']}' requires a field (e.g., 'sales', 'quantity')."
             intent["explanation_steps"].append(f"Error: Missing target field for '{intent['action']}'.")
             return intent
    elif intent["action"] == "count":
         intent["target_field"] = "rows" 
         intent["explanation_steps"].append("Action 'count' will count matching rows.")


    possible_filters = {
        "product": KEYWORDS["products"],
        "category": KEYWORDS["categories"],
        "region": KEYWORDS["regions"],
        "month": KEYWORDS["months"]
    }
    found_filters = {}
    for entity, values in possible_filters.items():
        for value in values:
            if f" {value} " in f" {query} " or query.endswith(f" {value}") or query.startswith(f"{value} "):
                if entity not in found_filters: 
                    found_filters[entity] = value
                    intent["explanation_steps"].append(f"Identified filter: {entity} = '{value}'.")

    intent["filters"] = found_filters

    if not found_filters and intent["action"] != 'count' and 'all' not in query:
         if intent["action"] in ["sum", "average"]:
             intent["explanation_steps"].append("Warning: Aggregation performed on all data as no filters were specified.")
         else:
             intent["explanation_steps"].append("Listing all data as no filters were specified.")

    select_clause = "*"
    if intent["action"] == "count":
        select_clause = "COUNT(*)"
    elif intent["action"] == "sum":
        select_clause = f"SUM({intent['target_field']})"
    elif intent["action"] == "average":
        select_clause = f"AVG({intent['target_field']})"

    where_clauses = []
    for field, value in intent["filters"].items():
        where_clauses.append(f"{field} = '{value}'")

    where_string = ""
    if where_clauses:
        where_string = " WHERE " + " AND ".join(where_clauses)

    intent["pseudo_sql"] = f"SELECT {select_clause} FROM sales{where_string} (simulated)"
    intent["explanation_steps"].append(f"Generated simulated query: {intent['pseudo_sql']}")

    if intent["action"] == "list" and not intent["filters"] and len(words) < 2: # Very short query might be invalid
         pass 

    intent["explanation_steps"].append("Query parsing complete.")
    return intent


def execute_query(intent):
    """ Executes the parsed intent against the mock database. """
    if not intent["valid"]:
        return {"error": intent["reason"]}

    filtered_data = mock_data_db
    if intent["filters"]:
        for field, value in intent["filters"].items():
            filtered_data = [row for row in filtered_data if field in row and str(row[field]).lower() == value.lower()]

    action = intent["action"]
    target_field = intent["target_field"]

    try:
        if action == "list":
            return {"result": filtered_data}
        elif action == "count":
            return {"result": len(filtered_data)}
        elif action == "sum":
            if not target_field: return {"error": "Missing field for sum."}
            total = sum(row.get(target_field, 0) for row in filtered_data if isinstance(row.get(target_field), (int, float)))
            return {"result": total}
        elif action == "average":
            if not target_field: return {"error": "Missing field for average."}
            values = [row.get(target_field, 0) for row in filtered_data if isinstance(row.get(target_field), (int, float))]
            if not values:
                return {"result": 0} 
            avg = sum(values) / len(values)
            return {"result": avg}
        else:
            return {"error": f"Action '{action}' execution not implemented."}
    except Exception as e:
        print(f"Error during query execution: {e}") 
        return {"error": "An internal error occurred during query execution."}