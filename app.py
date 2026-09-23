"""
Customer Support Intake & Routing System
-----------------------------------------
DEMO-ONLY mock CRM API.

This file simulates the CRM lookup used by the portfolio prototype.
It does NOT connect to a real CRM, database, authentication system,
or production infrastructure.
"""

from flask import Flask, jsonify, request

app = Flask(__name__)

DEMO_ORDERS = {
    84721: {
        "customer_id": 551,
        "status": "delivered",
    },
    84722: {
        "customer_id": 552,
        "status": "pending",
    },
}


@app.get("/crm/order")
def get_order():
    """Return deterministic mock CRM data for an order."""

    order_id_raw = request.args.get("order_id")
    customer_id_raw = request.args.get("customer_id")

    if not order_id_raw or not customer_id_raw:
        return jsonify({
            "error": "order_id and customer_id are required"
        }), 400

    try:
        order_id = int(order_id_raw)
        customer_id = int(customer_id_raw)
    except ValueError:
        return jsonify({
            "error": "order_id and customer_id must be integers"
        }), 400

    mock_order = DEMO_ORDERS.get(order_id)

    if mock_order is None:
        return jsonify({
            "error": "mock order not found"
        }), 404

    if mock_order["customer_id"] != customer_id:
        return jsonify({
            "error": "order does not belong to customer"
        }), 404

    return jsonify({
        "order_id": order_id,
        "customer_id": customer_id,
        "status": mock_order["status"],
    }), 200


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True)
