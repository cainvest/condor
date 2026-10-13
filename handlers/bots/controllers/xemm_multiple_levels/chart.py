"""
XEMM Multiple Levels chart generation.

Generates candlestick charts with spread level overlays:
- Buy levels (green dashed lines below mid price)
- Sell levels (red dashed lines above mid price)
- Current price line (orange solid)
"""

import io
from typing import Any, Dict, List, Optional

from handlers.dex.visualizations import DARK_THEME, generate_candlestick_chart


def _parse_levels(levels_str: str) -> List[tuple]:
    """Parse 'target,amount-target,amount-...' into list of (target, amount)."""
    result = []
    if not levels_str:
        return result
    for part in str(levels_str).split("-"):
        pieces = part.split(",")
        if len(pieces) == 2:
            try:
                result.append((float(pieces[0]), float(pieces[1])))
            except ValueError:
                continue
    return result


def generate_chart(
    config: Dict[str, Any],
    candles_data: List[Dict[str, Any]],
    current_price: Optional[float] = None,
) -> io.BytesIO:
    """
    Generate a candlestick chart with XEMM spread levels overlay.

    Shows buy levels below and sell levels above the current price.
    """
    maker_pair = config.get("maker_trading_pair", "Unknown")
    taker_connector = config.get("taker_connector", "unknown")

    data = (
        candles_data if isinstance(candles_data, list) else candles_data.get("data", [])
    )

    title = f"{maker_pair} - XEMM (taker: {taker_connector})"

    ref_price = current_price
    if not ref_price and data:
        last_candle = data[-1] if isinstance(data[-1], dict) else None
        if last_candle:
            ref_price = last_candle.get("close", 0)

    hlines = []

    if ref_price:
        buy_levels = _parse_levels(config.get("buy_levels_targets_amount", ""))
        for i, (target, amount) in enumerate(buy_levels):
            buy_price = ref_price * (1 - target)
            hlines.append({
                "y": buy_price,
                "color": DARK_THEME["up_color"],
                "dash": "dash",
                "width": 1.5,
                "label": f"B{i+1}: {buy_price:,.4f} (-{target*100:.3f}%, {amount:.0f})",
                "label_position": "left",
            })

        sell_levels = _parse_levels(config.get("sell_levels_targets_amount", ""))
        for i, (target, amount) in enumerate(sell_levels):
            sell_price = ref_price * (1 + target)
            hlines.append({
                "y": sell_price,
                "color": DARK_THEME["down_color"],
                "dash": "dash",
                "width": 1.5,
                "label": f"S{i+1}: {sell_price:,.4f} (+{target*100:.3f}%, {amount:.0f})",
                "label_position": "right",
            })

    result = generate_candlestick_chart(
        candles=data,
        title=title,
        current_price=current_price,
        show_volume=False,
        width=1100,
        height=500,
        hlines=hlines if hlines else None,
        hrects=None,
        reverse_data=False,
    )

    if result is None:
        import plotly.graph_objects as go

        fig = go.Figure()
        fig.add_annotation(
            text="No candle data available",
            xref="paper", yref="paper",
            x=0.5, y=0.5, showarrow=False,
            font=dict(
                family=DARK_THEME["font_family"],
                size=16,
                color=DARK_THEME["font_color"],
            ),
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME["paper_bgcolor"],
            plot_bgcolor=DARK_THEME["plot_bgcolor"],
            width=1100, height=500,
        )
        img_bytes = io.BytesIO()
        fig.write_image(img_bytes, format="png", scale=2)
        img_bytes.seek(0)
        return img_bytes

    return result


def generate_preview_chart(
    config: Dict[str, Any],
    candles_data: List[Dict[str, Any]],
    current_price: Optional[float] = None,
) -> io.BytesIO:
    """Generate a smaller preview chart for config viewing."""
    return generate_chart(config, candles_data, current_price)
