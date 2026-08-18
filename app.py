"""
Ðarlingtøn🦅 — Pi Network block explorer
Flask app, private Horizon node backend (46.250.230.8:31401)
"""

from flask import Flask, render_template, jsonify, request, abort
import horizon

app = Flask(__name__)

NETWORKS = ["mainnet", "testnet", "testnet2"]
ACTIVE_NETWORKS = ["mainnet"]  # only mainnet is wired for now


# ---------------------------------------------------------------------------
# Page routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    return render_template(
        "index.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/operations")
def operations_page():
    return render_template(
        "operations.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/payments")
def payments_page():
    return render_template(
        "payments.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/transactions")
def transactions_page():
    return render_template(
        "transactions.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/transactions/<tx_hash>")
def transaction_detail(tx_hash):
    return render_template(
        "transaction_detail.html",
        tx_hash=tx_hash,
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/blocks")
def blocks_page():
    return render_template(
        "blocks.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/blocks/<int:sequence>")
def block_detail(sequence):
    return render_template(
        "block_detail.html",
        sequence=sequence,
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/nodes")
def nodes_page():
    return render_template(
        "nodes.html",
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/account/<account_id>")
def account_detail(account_id):
    return render_template(
        "account_detail.html",
        account_id=account_id,
        networks=NETWORKS,
        active_networks=ACTIVE_NETWORKS,
        current_network="mainnet",
    )


@app.route("/search")
def search_page():
    q = request.args.get("q", "").strip()
    if not q:
        return render_template("search_results.html", query=q, kind=None, result=None)

    kind, result = horizon.search(q)

    if kind == "transaction":
        return render_template("transaction_detail.html", tx_hash=q,
                                networks=NETWORKS, active_networks=ACTIVE_NETWORKS,
                                current_network="mainnet")
    if kind == "ledger":
        return render_template("block_detail.html", sequence=int(q),
                                networks=NETWORKS, active_networks=ACTIVE_NETWORKS,
                                current_network="mainnet")
    if kind == "account":
        return render_template("account_detail.html", account_id=q,
                                networks=NETWORKS, active_networks=ACTIVE_NETWORKS,
                                current_network="mainnet")

    return render_template("search_results.html", query=q, kind=None, result=None,
                            networks=NETWORKS, active_networks=ACTIVE_NETWORKS,
                            current_network="mainnet")


# ---------------------------------------------------------------------------
# JSON API routes (consumed by frontend JS for live feed + pagination)
# ---------------------------------------------------------------------------

@app.route("/api/ledgers")
def api_ledgers():
    limit = min(int(request.args.get("limit", 20)), 100)
    cursor = request.args.get("cursor")
    try:
        records = horizon.get_ledgers(limit=limit, cursor=cursor)
        return jsonify({"ok": True, "records": records})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/ledgers/<int:sequence>")
def api_ledger_detail(sequence):
    try:
        ledger = horizon.get_ledger(sequence)
        txs = horizon.get_transactions_for_ledger(sequence)
        return jsonify({"ok": True, "ledger": ledger, "transactions": txs})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/transactions")
def api_transactions():
    limit = min(int(request.args.get("limit", 20)), 100)
    cursor = request.args.get("cursor")
    try:
        records = horizon.get_transactions(limit=limit, cursor=cursor)
        return jsonify({"ok": True, "records": records})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/transactions/<tx_hash>")
def api_transaction_detail(tx_hash):
    try:
        tx = horizon.get_transaction(tx_hash)
        ops = horizon.get_operations_for_transaction(tx_hash)
        return jsonify({"ok": True, "transaction": tx, "operations": ops})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/operations")
def api_operations():
    limit = min(int(request.args.get("limit", 20)), 100)
    cursor = request.args.get("cursor")
    try:
        records = horizon.get_operations(limit=limit, cursor=cursor)
        return jsonify({"ok": True, "records": records})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/payments")
def api_payments():
    limit = min(int(request.args.get("limit", 20)), 100)
    cursor = request.args.get("cursor")
    try:
        records = horizon.get_payments(limit=limit, cursor=cursor)
        return jsonify({"ok": True, "records": records})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/accounts/<account_id>")
def api_account_detail(account_id):
    try:
        account = horizon.get_account(account_id)
        payments = horizon.get_payments_for_account(account_id)
        txs = horizon.get_transactions_for_account(account_id)
        return jsonify({"ok": True, "account": account, "payments": payments, "transactions": txs})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/node-status")
def api_node_status():
    try:
        status = horizon.get_node_status()
        return jsonify({"ok": True, "status": status})
    except horizon.HorizonError as e:
        return jsonify({"ok": False, "error": str(e)}), 502


@app.route("/api/search")
def api_search():
    q = request.args.get("q", "").strip()
    kind, result = horizon.search(q)
    if kind is None:
        return jsonify({"ok": False, "error": "No matching transaction, ledger, or account found"}), 404
    return jsonify({"ok": True, "kind": kind, "result": result})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3060, debug=False)
