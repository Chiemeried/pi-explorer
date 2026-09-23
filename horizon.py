"""
horizon.py
Thin wrapper around the private Pi Network Horizon node, with automatic
fallback to the public mainnet Horizon API for old ledgers/transactions
that have aged out of the private node's history retention window.
"""

import requests

HORIZON_BASE = "http://46.250.230.8:31401"
PUBLIC_HORIZON_BASE = "https://api.mainnet.minepi.com"
TIMEOUT = 8  # seconds


class HorizonError(Exception):
    pass


def _get_from(base, path, params=None):
    url = f"{base}{path}"
    resp = requests.get(url, params=params, timeout=TIMEOUT)
    resp.raise_for_status()
    return resp.json()


def _get(path, params=None, allow_fallback=True):
    """
    Try the private node first. If it 404s (not found — likely aged out
    of local retention) or is unreachable, fall back to the public API
    when allow_fallback is True. List endpoints (recent feeds) should
    NOT fall back, since the public API has its own independent pagination
    and mixing sources there would produce confusing results.
    """
    try:
        return _get_from(HORIZON_BASE, path, params), "private"
    except requests.exceptions.HTTPError as e:
        status = e.response.status_code if e.response is not None else None
        if allow_fallback and status in (404, 410):
            try:
                return _get_from(PUBLIC_HORIZON_BASE, path, params), "public"
            except requests.exceptions.RequestException as e2:
                raise HorizonError(f"Not found on private node, public fallback failed: {e2}") from e2
        raise HorizonError(f"Horizon request failed ({status}): {e}") from e
    except requests.exceptions.RequestException as e:
        if allow_fallback:
            try:
                return _get_from(PUBLIC_HORIZON_BASE, path, params), "public"
            except requests.exceptions.RequestException as e2:
                raise HorizonError(f"Private node unreachable, public fallback failed: {e2}") from e2
        raise HorizonError(f"Horizon request failed: {e}") from e


# ---------- Ledgers (Blocks) ----------

def get_ledgers(limit=20, cursor=None, order="desc"):
    """Recent feed — private node only, no fallback (keeps pagination consistent)."""
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data, _ = _get("/ledgers", params, allow_fallback=False)
    return data.get("_embedded", {}).get("records", [])


def get_ledger(sequence):
    """Single ledger lookup — falls back to public API if aged out of local retention."""
    data, source = _get(f"/ledgers/{sequence}")
    data["_source"] = source
    return data


# ---------- Transactions ----------

def get_transactions(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data, _ = _get("/transactions", params, allow_fallback=False)
    return data.get("_embedded", {}).get("records", [])


def get_transaction(tx_hash):
    data, source = _get(f"/transactions/{tx_hash}")
    data["_source"] = source
    return data


def get_transactions_for_ledger(sequence, limit=20):
    data, _ = _get(f"/ledgers/{sequence}/transactions", {"limit": limit})
    return data.get("_embedded", {}).get("records", [])


# ---------- Operations ----------

def get_operations(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data, _ = _get("/operations", params, allow_fallback=False)
    return data.get("_embedded", {}).get("records", [])


def get_operations_for_transaction(tx_hash):
    data, _ = _get(f"/transactions/{tx_hash}/operations")
    return data.get("_embedded", {}).get("records", [])


# ---------- Payments ----------

def get_payments(limit=20, cursor=None, order="desc"):
    params = {"limit": limit, "order": order}
    if cursor:
        params["cursor"] = cursor
    data, _ = _get("/payments", params, allow_fallback=False)
    return data.get("_embedded", {}).get("records", [])


# ---------- Accounts ----------

def get_account(account_id):
    data, source = _get(f"/accounts/{account_id}")
    data["_source"] = source
    return data


def get_payments_for_account(account_id, limit=20):
    data, _ = _get(f"/accounts/{account_id}/payments", {"limit": limit, "order": "desc"})
    return data.get("_embedded", {}).get("records", [])


def get_transactions_for_account(account_id, limit=20):
    data, _ = _get(f"/accounts/{account_id}/transactions", {"limit": limit, "order": "desc"})
    return data.get("_embedded", {}).get("records", [])


# ---------- Nodes ----------

def get_node_status():
    """Root endpoint returns core node / network info. Private node only."""
    data, _ = _get("/", allow_fallback=False)
    return data


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
