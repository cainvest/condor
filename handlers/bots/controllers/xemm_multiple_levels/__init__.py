"""
XEMM Multiple Levels Controller Module

Cross-exchange market making with multiple spread levels.
- Places limit orders on a maker exchange (e.g. Binance)
- Hedges fills on a taker exchange (e.g. cainvest_spot)
- Supports multiple spread levels with configurable amounts
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


class XemmMultipleLevelsController(BaseController):
    """XEMM Multiple Levels controller implementation."""

    controller_type = "xemm_multiple_levels"
    display_name = "XEMM Multiple Levels"
    description = "Cross-exchange market making with multiple spread levels"

    @classmethod
    def get_defaults(cls) -> Dict[str, Any]:
        return DEFAULTS.copy()

    @classmethod
    def get_fields(cls) -> Dict[str, ControllerField]:
        return FIELDS

    @classmethod
    def get_field_order(cls) -> List[str]:
        return FIELD_ORDER

    @classmethod
    def validate_config(cls, config: Dict[str, Any]) -> Tuple[bool, Optional[str]]:
        return validate_config(config)

    @classmethod
    def generate_chart(
        cls,
        config: Dict[str, Any],
        candles_data: List[Dict[str, Any]],
        current_price: Optional[float] = None,
    ) -> io.BytesIO:
        return generate_chart(config, candles_data, current_price)

    @classmethod
    def generate_id(
        cls, config: Dict[str, Any], existing_configs: List[Dict[str, Any]]
    ) -> str:
        return generate_id(config, existing_configs)


__all__ = [
    "XemmMultipleLevelsController",
    "DEFAULTS",
    "FIELDS",
    "FIELD_ORDER",
    "WIZARD_STEPS",
    "validate_config",
    "generate_id",
    "generate_chart",
    "generate_preview_chart",
]
