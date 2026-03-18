"""
Cainvest MM Controller Module

Provides configuration, validation, and visualization for the Cainvest Market Maker controller.

Cainvest MM:
- Streams reference prices from Cainvest WebSocket (USDC/BRL)
- Places spread-adjusted LIMIT_MAKER orders on a CEX (e.g. Binance)
- Hedges fills through the Cainvest Quotes API (inverse direction)
"""

import io
from typing import Any, Dict, List, Optional, Tuple

from .._base import BaseController, ControllerField
from .chart import generate_chart, generate_preview_chart
from .config import (
    DEFAULTS,
    FIELD_ORDER,
    FIELDS,
    WIZARD_STEPS,
    generate_id,
    validate_config,
)


class CainvestMMController(BaseController):
    """Cainvest Market Maker controller implementation."""

    controller_type = "cainvest_mm"
    display_name = "Cainvest MM"
    description = "Market making with Cainvest reference prices and automatic hedging"

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        """Get default configuration values."""
        return DEFAULTS.copy()

    @classmethod
    def get_fields(cls) -> Dict[str, ControllerField]:
        """Get field definitions."""
        return FIELDS

    @classmethod
    def get_field_order(cls) -> List[str]:
        """Get field display order."""
        return FIELD_ORDER

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        """Validate configuration."""
        return validate_config(config)

    @classmethod
    def generate_chart(
        cls,
        config: Dict[str, Any],
        candles_data: List[Dict[str, Any]],
        current_price: Optional[float] = None,
    ) -> io.BytesIO:
        """Generate visualization chart."""
        return generate_chart(config, candles_data, current_price)

    @classmethod
    def generate_id(
        cls, config: Dict[str, Any], existing_configs: List[Dict[str, Any]]
    ) -> str:
        """Generate unique ID with sequence number."""
        return generate_id(config, existing_configs)


__all__ = [
    "CainvestMMController",
    "DEFAULTS",
    "FIELDS",
    "FIELD_ORDER",
    "WIZARD_STEPS",
    "validate_config",
    "generate_id",
    "generate_chart",
    "generate_preview_chart",
]
