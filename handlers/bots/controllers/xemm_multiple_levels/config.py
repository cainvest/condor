"""
XEMM Multiple Levels controller configuration.

Cross-exchange market making with multiple spread levels.
Maker orders on one exchange, taker hedge on another.
"""

from typing import Any, Dict, List, Optional, Tuple

from .._base import ControllerField

DEFAULTS: Dict[str, Any] = {
    "controller_name": "xemm_multiple_levels",
    "controller_type": "generic",
    "id": "",
    "maker_connector": "binance",
    "maker_trading_pair": "USDC-BRL",
    "taker_connector": "cainvest_spot",
    "taker_trading_pair": "USDC-BRL",
    "buy_levels_targets_amount": "0.0001,10-0.0001,10-0.0002,20",
    "sell_levels_targets_amount": "0.0001,10-0.0001,10-0.0002,20",
    "min_profitability": "0.00005",
    "max_profitability": "0.0001",
    "max_executors_imbalance": 1,
    "total_amount_quote": "1000",
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
    "maker_connector": ControllerField(
        name="maker_connector",
        label="Maker Exchange",
        type="str",
        required=True,
        hint="Exchange for limit orders (e.g. binance)",
    ),
    "maker_trading_pair": ControllerField(
        name="maker_trading_pair",
        label="Maker Pair",
        type="str",
        required=True,
        hint="Trading pair on maker (e.g. USDC-BRL)",
    ),
    "taker_connector": ControllerField(
        name="taker_connector",
        label="Taker Exchange",
        type="str",
        required=True,
        hint="Exchange for hedge/reference (e.g. cainvest_spot)",
    ),
    "taker_trading_pair": ControllerField(
        name="taker_trading_pair",
        label="Taker Pair",
        type="str",
        required=True,
        hint="Trading pair on taker (e.g. USDC-BRL)",
    ),
    "buy_levels_targets_amount": ControllerField(
        name="buy_levels_targets_amount",
        label="Buy Levels",
        type="str",
        required=True,
        hint="target,amount per level separated by - (e.g. 0.0001,10-0.0002,20)",
        default="0.0001,10-0.0001,10-0.0002,20",
    ),
    "sell_levels_targets_amount": ControllerField(
        name="sell_levels_targets_amount",
        label="Sell Levels",
        type="str",
        required=True,
        hint="target,amount per level separated by - (e.g. 0.0001,10-0.0002,20)",
        default="0.0001,10-0.0001,10-0.0002,20",
    ),
    "min_profitability": ControllerField(
        name="min_profitability",
        label="Min Profitability",
        type="str",
        required=True,
        hint="Margin below target to cancel executor (e.g. 0.00005 = 0.5bp)",
        default="0.00005",
    ),
    "max_profitability": ControllerField(
        name="max_profitability",
        label="Max Profitability",
        type="str",
        required=True,
        hint="Margin above target for spread ceiling (e.g. 0.0001 = 1bp)",
        default="0.0001",
    ),
    "max_executors_imbalance": ControllerField(
        name="max_executors_imbalance",
        label="Max Imbalance",
        type="int",
        required=False,
        hint="Max buy-sell executor imbalance (default: 1)",
        default=1,
    ),
    "total_amount_quote": ControllerField(
        name="total_amount_quote",
        label="Total Quote Amount",
        type="str",
        required=True,
        hint="Total capital in quote (BRL), split 50/50 buy/sell",
        default="1000",
    ),
    "manual_kill_switch": ControllerField(
        name="manual_kill_switch",
        label="Kill Switch",
        type="bool",
        required=False,
        hint="Stop creating new executors when enabled",
        default=False,
    ),
}


FIELD_ORDER: List[str] = [
    "id",
    "maker_connector",
    "maker_trading_pair",
    "taker_connector",
    "taker_trading_pair",
    "buy_levels_targets_amount",
    "sell_levels_targets_amount",
    "min_profitability",
    "max_profitability",
    "max_executors_imbalance",
    "total_amount_quote",
    "manual_kill_switch",
]


WIZARD_STEPS: List[str] = [
    "maker_connector",
    "maker_trading_pair",
    "taker_connector",
    "taker_trading_pair",
    "buy_levels_targets_amount",
    "sell_levels_targets_amount",
    "profitability",
    "review",
]


def validate_config(config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
    """Validate an XEMM Multiple Levels configuration."""
    required = ["maker_connector", "maker_trading_pair", "taker_connector", "taker_trading_pair"]
    for field in required:
        if not config.get(field):
            return False, f"Missing required field: {field}"

    for field_name in ["buy_levels_targets_amount", "sell_levels_targets_amount"]:
        val = config.get(field_name, "")
        if not val:
            return False, f"Missing required field: {field_name}"
        try:
            for level in str(val).split("-"):
                parts = level.split(",")
                if len(parts) != 2:
                    return False, f"Invalid level format in {field_name}: '{level}' (expected target,amount)"
                float(parts[0])
                float(parts[1])
        except (ValueError, TypeError):
            return False, f"Invalid numeric values in {field_name}: {val}"

    for field_name in ["min_profitability", "max_profitability"]:
        val = config.get(field_name, "0")
        try:
            v = float(val)
            if v < 0:
                return False, f"{field_name} must be non-negative"
        except (ValueError, TypeError):
            return False, f"Invalid {field_name}: {val}"

    total = config.get("total_amount_quote", "0")
    try:
        t = float(total)
        if t <= 0:
            return False, "total_amount_quote must be positive"
    except (ValueError, TypeError):
        return False, f"Invalid total_amount_quote: {total}"

    return True, None


def generate_id(config: Dict[str, Any], existing_configs: List[Dict[str, Any]]) -> str:
    """
    Generate a unique config ID with sequential numbering.

    Format: NNN_xemm_maker_taker_pair
    Example: 003_xemm_binance_cainvest_USDC-BRL
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

    maker = config.get("maker_connector", "unknown")
    maker_clean = maker.replace("_perpetual", "").replace("_spot", "")
    taker = config.get("taker_connector", "unknown")
    taker_clean = taker.replace("_perpetual", "").replace("_spot", "")
    pair = config.get("maker_trading_pair", "UNKNOWN").upper()

    return f"{seq}_xemm_{maker_clean}_{taker_clean}_{pair}"
