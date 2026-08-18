"""
horizon.py
Thin wrapper around the private Pi Network Horizon node.
No rate limiting on this node, so we can poll it freely.
"""

import requests

HORIZON_BASE = "http://46.250.230.8:31401"
TIMEOUT = 8  # seconds


class HorizonError(Exception):
    pass


def _get(path, params=None):
    url = f"{HORIZON_BASE}{path}"
    try:
        resp = requests.get(url, params=params, timeout=TIMEOUT)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        raise HorizonError(f"Horizon request failed: {e}") from e


# ---------- Ledgers (Blocks) ----------

def get_ledgers(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data = _get("/ledgers", params)
    return data.get("_embedded", {}).get("records", [])


def get_ledger(sequence):
    return _get(f"/ledgers/{sequence}")


# ---------- Transactions ----------

def get_transactions(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data = _get("/transactions", params)
    return data.get("_embedded", {}).get("records", [])


def get_transaction(tx_hash):
    return _get(f"/transactions/{tx_hash}")


def get_transactions_for_ledger(sequence, limit=20):
    data = _get(f"/ledgers/{sequence}/transactions", {"limit": limit})
    return data.get("_embedded", {}).get("records", [])


# ---------- Operations ----------

def get_operations(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data = _get("/operations", params)
    return data.get("_embedded", {}).get("records", [])


def get_operations_for_transaction(tx_hash):
    data = _get(f"/transactions/{tx_hash}/operations")
    return data.get("_embedded", {}).get("records", [])


# ---------- Payments ----------

def get_payments(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data = _get("/payments", params)
    return data.get("_embedded", {}).get("records", [])


# ---------- Accounts ----------

def get_account(account_id):
    return _get(f"/accounts/{account_id}")


def get_payments_for_account(account_id, limit=20):
    data = _get(f"/accounts/{account_id}/payments", {"limit": limit, "order": "desc"})
    return data.get("_embedded", {}).get("records", [])


def get_transactions_for_account(account_id, limit=20):
    data = _get(f"/accounts/{account_id}/transactions", {"limit": limit, "order": "desc"})
    return data.get("_embedded", {}).get("records", [])


# ---------- Nodes ----------

def get_node_status():
    """Root endpoint returns core node / network info."""
    return _get("/")


# ---------- Search dispatch ----------

def search(query):
    """
    Try to resolve a search query to the right resource type.
    Returns (kind, data) or (None, None) if nothing found.
    """
    query = query.strip()
    if not query:
        return None, None

    # Transaction hash: 64 hex chars
    if len(query) == 64 and all(c in "0123456789abcdefABCDEF" for c in query):
        try:
            return "transaction", get_transaction(query)
        except HorizonError:
            pass

    # Ledger sequence: numeric
    if query.isdigit():
        try:
            return "ledger", get_ledger(int(query))
        except HorizonError:
            pass

    # Account: starts with G, 56 chars (Stellar/Pi address format)
    if query.startswith("G") and len(query) == 56:
        try:
            return "account", get_account(query)
        except HorizonError:
            pass

    return None, None
