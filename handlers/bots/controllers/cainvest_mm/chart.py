"""
Cainvest MM chart generation.

Generates candlestick charts with Cainvest MM spread visualization:
- Buy spread level (green dashed line below reference)
- Sell spread level (red dashed line above reference)
- Current price line (orange solid)

Uses the unified candlestick chart function from visualizations module.
"""

import io
from typing import Any, Dict, List, Optional

from handlers.dex.visualizations import DARK_THEME, generate_candlestick_chart


def generate_chart(
    config: Dict[str, Any],
    candles_data: List[Dict[str, Any]],
    current_price: Optional[float] = None,
) -> io.BytesIO:
    """
    Generate a candlestick chart with Cainvest MM spread overlay.

    Shows:
    - Candlestick price data
    - Buy spread level (green dashed line below price)
    - Sell spread level (red dashed line above price)
    - Current price line (orange solid)

    Args:
        config: Cainvest MM configuration with spreads
        candles_data: List of candles from API (each with open, high, low, close, timestamp)
        current_price: Current market price

    Returns:
        BytesIO object containing the PNG image
    """
    trading_pair = config.get("trading_pair", "Unknown")

    buy_spread = float(config.get("buy_spread", 0.003))
    sell_spread = float(config.get("sell_spread", 0.003))

    data = (
        candles_data if isinstance(candles_data, list) else candles_data.get("data", [])
    )

    title = f"{trading_pair} - Cainvest MM"

    ref_price = current_price
    if not ref_price and data:
        last_candle = data[-1] if isinstance(data[-1], dict) else None
        if last_candle:
            ref_price = last_candle.get("close", 0)

    hlines = []

    if ref_price and buy_spread:
        buy_price = ref_price * (1 - buy_spread)
        hlines.append(
            {
                "y": buy_price,
                "color": DARK_THEME["up_color"],
                "dash": "dash",
                "width": 2,
                "label": f"Buy: {buy_price:,.4f} (-{buy_spread*100:.2f}%)",
                "label_position": "left",
            }
        )

    if ref_price and sell_spread:
        sell_price = ref_price * (1 + sell_spread)
        hlines.append(
            {
                "y": sell_price,
                "color": DARK_THEME["down_color"],
                "dash": "dash",
                "width": 2,
                "label": f"Sell: {sell_price:,.4f} (+{sell_spread*100:.2f}%)",
                "label_position": "right",
            }
        )

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
            xref="paper",
            yref="paper",
            x=0.5,
            y=0.5,
            showarrow=False,
            font=dict(
                family=DARK_THEME["font_family"],
                size=16,
                color=DARK_THEME["font_color"],
            ),
        )
        fig.update_layout(
            paper_bgcolor=DARK_THEME["paper_bgcolor"],
            plot_bgcolor=DARK_THEME["plot_bgcolor"],
            width=1100,
            height=500,
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
