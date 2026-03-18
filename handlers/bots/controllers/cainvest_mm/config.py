"""
Cainvest MM controller configuration.

Contains defaults, field definitions, and validation for the Cainvest Market Maker controller.
Streams Cainvest reference prices, places spread-adjusted orders on a CEX, and hedges fills
through the Cainvest Quotes API.
"""

from typing import Any, Dict, List, Optional, Tuple

from .._base import ControllerField

DEFAULTS: Dict[str, Any] = {
    "controller_name": "cainvest_mm",
    "controller_type": "generic",
    "id": "",
    "connector_name": "binance",
    "trading_pair": "USDC-BRL",
    "order_amount": "100",
    "buy_spread": "0.003",
    "sell_spread": "0.003",
    "order_refresh_time": 300,
    "cainvest_ws_url": "wss://api.spot.cainvest.io/ws",
    "cainvest_api_url": "https://api.spot.cainvest.io/api/v1",
    "cainvest_api_key": "",
    "cainvest_api_secret": "",
    "cainvest_currency_pair": "USDC/BRL",
    "settlement_date": "D0",
    "hedge_mode": "fill_events",
    "manual_kill_switch": False,
}


FIELDS: Dict[str, ControllerField] = {
    "id": ControllerField(
        name="id",
        label="Config ID",
        type="str",
        required=True,
        hint="Auto-generated with sequence number",
    ),
    "connector_name": ControllerField(
        name="connector_name",
        label="Connector",
        type="str",
        required=True,
        hint="Exchange connector (e.g. binance)",
    ),
    "trading_pair": ControllerField(
        name="trading_pair",
        label="Trading Pair",
        type="str",
        required=True,
        hint="Pair on the exchange (e.g. USDC-BRL)",
    ),
    "order_amount": ControllerField(
        name="order_amount",
        label="Order Amount (Base)",
        type="str",
        required=True,
        hint="Amount per order in base asset (e.g. 100 USDC)",
        default="100",
    ),
    "buy_spread": ControllerField(
        name="buy_spread",
        label="Buy Spread",
        type="str",
        required=True,
        hint="Spread below reference for buys (e.g. 0.003 = 0.3%)",
        default="0.003",
    ),
    "sell_spread": ControllerField(
        name="sell_spread",
        label="Sell Spread",
        type="str",
        required=True,
        hint="Spread above reference for sells (e.g. 0.003 = 0.3%)",
        default="0.003",
    ),
    "order_refresh_time": ControllerField(
        name="order_refresh_time",
        label="Refresh Time (s)",
        type="int",
        required=False,
        hint="Max seconds before force-refreshing orders (default: 300)",
        default=300,
    ),
    "cainvest_ws_url": ControllerField(
        name="cainvest_ws_url",
        label="Cainvest WS URL",
        type="str",
        required=True,
        hint="wss://api.spot.cainvest.io/ws or sandbox",
        default="wss://api.spot.cainvest.io/ws",
    ),
    "cainvest_api_url": ControllerField(
        name="cainvest_api_url",
        label="Cainvest API URL",
        type="str",
        required=True,
        hint="https://api.spot.cainvest.io/api/v1 or sandbox",
        default="https://api.spot.cainvest.io/api/v1",
    ),
    "cainvest_api_key": ControllerField(
        name="cainvest_api_key",
        label="Cainvest API Key",
        type="str",
        required=True,
        hint="Starts with ak_...",
    ),
    "cainvest_api_secret": ControllerField(
        name="cainvest_api_secret",
        label="Cainvest API Secret",
        type="str",
        required=True,
        hint="Starts with sk_...",
    ),
    "cainvest_currency_pair": ControllerField(
        name="cainvest_currency_pair",
        label="Cainvest Pair",
        type="str",
        required=True,
        hint="Currency pair on Cainvest (e.g. USDC/BRL)",
        default="USDC/BRL",
    ),
    "settlement_date": ControllerField(
        name="settlement_date",
        label="Settlement Date",
        type="str",
        required=False,
        hint="D0 (same day) or D1 (next day)",
        default="D0",
    ),
    "hedge_mode": ControllerField(
        name="hedge_mode",
        label="Hedge Mode",
        type="str",
        required=False,
        hint="fill_events (hedge each partial fill) or order_done (hedge when order completes)",
        default="fill_events",
    ),
    "manual_kill_switch": ControllerField(
        name="manual_kill_switch",
        label="Kill Switch",
        type="bool",
        required=False,
        hint="Manual kill switch to stop trading",
        default=False,
    ),
}


FIELD_ORDER: List[str] = [
    "id",
    "connector_name",
    "trading_pair",
    "order_amount",
    "buy_spread",
    "sell_spread",
    "order_refresh_time",
    "cainvest_ws_url",
    "cainvest_api_url",
    "cainvest_api_key",
    "cainvest_api_secret",
    "cainvest_currency_pair",
    "settlement_date",
    "hedge_mode",
    "manual_kill_switch",
]


WIZARD_STEPS: List[str] = [
    "connector_name",
    "trading_pair",
    "order_amount",
    "spreads",
    "hedge_mode",
    "cainvest_credentials",
    "review",
]


def validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """
    Validate a Cainvest MM configuration.

    Returns:
        Tuple of (is_valid, error_message)
    """
    required = ["connector_name", "trading_pair", "cainvest_api_key", "cainvest_api_secret"]
    for field in required:
        if not config.get(field):
            return False, f"Missing required field: {field}"

    # Validate order amount
    order_amount = config.get("order_amount", "100")
    try:
        amt = float(order_amount)
        if amt <= 0:
            return False, "Order amount must be positive"
    except (ValueError, TypeError):
        return False, f"Invalid order amount: {order_amount}"

    # Validate spreads
    for field_name in ["buy_spread", "sell_spread"]:
        val = config.get(field_name, "0.003")
        try:
            spread = float(val)
            if spread < 0:
                return False, f"{field_name} must be non-negative"
        except (ValueError, TypeError):
            return False, f"Invalid {field_name}: {val}"

    # Validate Cainvest credentials format
    api_key = config.get("cainvest_api_key", "")
    if api_key and not api_key.startswith("ak_"):
        return False, "Cainvest API key should start with 'ak_'"

    api_secret = config.get("cainvest_api_secret", "")
    if api_secret and not api_secret.startswith("sk_"):
        return False, "Cainvest API secret should start with 'sk_'"

    # Validate settlement date
    settlement = config.get("settlement_date", "D0")
    if settlement not in ("D0", "D1"):
        return False, f"Settlement date must be D0 or D1, got: {settlement}"

    # Validate hedge mode
    hedge_mode = config.get("hedge_mode", "fill_events")
    if hedge_mode not in ("fill_events", "order_done"):
        return False, f"hedge_mode must be 'fill_events' or 'order_done', got: {hedge_mode}"

    return True, None


def generate_id(config: Dict[str, Any], existing_configs: List[Dict[str, Any]]) -> str:
    """
    Generate a unique config ID with sequential numbering.

    Format: NNN_cmm_connector_pair
    Example: 001_cmm_binance_USDC-BRL
    """
    max_num = 0
    for cfg in existing_configs:
        config_id = cfg.get("id", "")
        if not config_id:
            continue
        parts = config_id.split("_", 1)
        if parts and parts[0].isdigit():
            max_num = max(max_num, int(parts[0]))

    seq = str(max_num + 1).zfill(3)

    connector = config.get("connector_name", "unknown")
    conn_clean = connector.replace("_perpetual", "").replace("_spot", "")
    pair = config.get("trading_pair", "UNKNOWN").upper()

    return f"{seq}_cmm_{conn_clean}_{pair}"
