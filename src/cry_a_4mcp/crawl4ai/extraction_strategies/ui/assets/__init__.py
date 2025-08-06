"""UI assets for the Strategy Manager UI.

This package provides assets for the Strategy Manager UI, including:
- Custom CSS styles
- SVG icons
- UI utility functions
"""

from .ui_utils import (
    load_css,
    get_icon,
    render_nav_item,
    render_action_button,
    render_status_indicator,
    render_app_header,
    render_strategy_card,
    render_search_box,
    render_tooltip,
    render_metric_card
)

from .icons import get_all_icons

__all__ = [
    'load_css',
    'get_icon',
    'get_all_icons',
    'render_nav_item',
    'render_action_button',
    'render_status_indicator',
    'render_app_header',
    'render_strategy_card',
    'render_search_box',
    'render_tooltip',
    'render_metric_card'
]