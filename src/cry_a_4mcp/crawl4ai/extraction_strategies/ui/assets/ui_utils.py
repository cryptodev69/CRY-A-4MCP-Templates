"""UI utilities for the Strategy Manager UI.

This module provides utility functions for enhancing the UI of the Strategy Manager.
"""

import streamlit as st
from pathlib import Path
import logging

# Import icons
from .icons import get_all_icons

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def load_css():
    """Load custom CSS for the Strategy Manager UI."""
    try:
        css_file = Path(__file__).parent / "custom.css"
        with open(css_file, "r") as f:
            css = f.read()
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
            logger.info("Custom CSS loaded successfully")
    except Exception as e:
        logger.error(f"Error loading custom CSS: {e}")
        # Fallback CSS if file can't be loaded
        st.markdown("""
        <style>
        .main-nav .nav-item {
            padding: 0.5rem 1rem;
            border-radius: 0.5rem;
            margin-bottom: 0.5rem;
            transition: background-color 0.3s;
        }
        .main-nav .nav-item:hover {
            background-color: rgba(237, 237, 237, 0.1);
        }
        .main-nav .nav-item.active {
            background-color: rgba(237, 237, 237, 0.2);
            font-weight: bold;
        }
        </style>
        """, unsafe_allow_html=True)


def get_icon(icon_name):
    """Get an icon by name.
    
    Args:
        icon_name: The name of the icon to get.
        
    Returns:
        The SVG icon as a string.
    """
    icons = get_all_icons()
    return icons.get(icon_name, "")


def render_nav_item(label, icon_name, page_id, active=False):
    """Render a navigation item with an icon.
    
    Args:
        label: The label for the navigation item.
        icon_name: The name of the icon to use.
        page_id: The ID of the page to navigate to.
        active: Whether the navigation item is active.
        
    Returns:
        A Streamlit button for the navigation item.
    """
    icon = get_icon(icon_name)
    active_class = "active" if active else ""
    
    # Create the HTML for the navigation item
    nav_html = f"""
    <div class="nav-item {active_class}">
        <div class="nav-icon">{icon}</div>
        <div>{label}</div>
    </div>
    """
    
    # Create a button with the navigation item HTML
    if st.sidebar.button(
        label, 
        key=f"nav_{page_id}", 
        help=f"Go to {label}", 
        use_container_width=True
    ):
        st.session_state.page = page_id
        # Clear any temporary session state when changing pages
        for key in list(st.session_state.keys()):
            if key.startswith("temp_"):
                del st.session_state[key]
        # Force a rerun to apply the navigation change immediately
        st.rerun()


def render_action_button(label, icon_name, key, help_text="", on_click=None, args=None, kwargs=None):
    """Render an action button with an icon.
    
    Args:
        label: The label for the button.
        icon_name: The name of the icon to use.
        key: The key for the button.
        help_text: The help text for the button.
        on_click: The function to call when the button is clicked.
        args: The arguments to pass to the on_click function.
        kwargs: The keyword arguments to pass to the on_click function.
        
    Returns:
        A Streamlit button for the action.
    """
    icon = get_icon(icon_name)
    
    # Create the HTML for the button
    button_html = f"""
    <div class="action-button-content">
        <div class="action-icon">{icon}</div>
        <div>{label}</div>
    </div>
    """
    
    # Create a button with the action button HTML
    return st.button(
        label,
        key=key,
        help=help_text,
        on_click=on_click,
        args=args or (),
        kwargs=kwargs or {}
    )


def render_status_indicator(status, text=""):
    """Render a status indicator.
    
    Args:
        status: The status to indicate (success, warning, error, info).
        text: The text to display with the status indicator.
        
    Returns:
        HTML for the status indicator.
    """
    icon_name = f"{status.lower()}"
    icon = get_icon(icon_name)
    
    # Create the HTML for the status indicator
    status_html = f"""
    <div class="status-indicator-container">
        <div class="status-indicator {status.lower()}">{icon}</div>
        <div class="status-text">{text}</div>
    </div>
    """
    
    return st.markdown(status_html, unsafe_allow_html=True)


def render_app_header(title="Extraction Strategy Manager", subtitle=""):
    """Render the application header with logo.
    
    Args:
        title: The title to display in the header.
        subtitle: The subtitle to display in the header.
    """
    logo = get_icon("app_logo")
    
    # Create the HTML for the header
    header_html = f"""
    <div class="app-header">
        <div class="app-logo">{logo}</div>
        <div class="app-title-container">
            <div class="app-title">{title}</div>
            {f'<div class="app-subtitle">{subtitle}</div>' if subtitle else ''}
        </div>
    </div>
    """
    
    st.markdown(header_html, unsafe_allow_html=True)


def render_strategy_card(strategy, index):
    """Render a strategy card.
    
    Args:
        strategy: The strategy data to render.
        index: The index of the strategy for generating unique keys.
        
    Returns:
        A Streamlit container with the strategy card.
    """
    with st.container():
        st.markdown(f"<div class='strategy-card'>\n", unsafe_allow_html=True)
        
        # Strategy header
        st.subheader(strategy['name'])
        
        # Category badge
        category = strategy.get('category', 'general')
        st.markdown(f"<div class='category-badge'>{category}</div>", unsafe_allow_html=True)
        
        # Description
        st.write(strategy['description'])
        
        # Provider info
        st.write(f"Default Provider: {strategy.get('default_provider', 'Not specified')}")
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if render_action_button(
                "Edit", "edit", f"edit_{index}", "Edit this strategy"
            ):
                st.session_state.temp_edit_strategy = strategy['name']
                st.session_state.page = "edit_strategy"
                st.rerun()
        
        with col2:
            if render_action_button(
                "Test", "test_action", f"test_{index}", "Test this strategy"
            ):
                st.session_state.temp_test_strategy = strategy['name']
                st.session_state.page = "test"
                st.rerun()
        
        with col3:
            if render_action_button(
                "Code", "view_code", f"code_{index}", "View strategy code"
            ):
                st.session_state.view_code = True
                st.session_state.selected_strategy = strategy['name']
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_search_box(placeholder="Search strategies..."):
    """Render a search box with an icon.
    
    Args:
        placeholder: The placeholder text for the search box.
        
    Returns:
        The search query entered by the user.
    """
    search_icon = get_icon("search")
    
    # Create the HTML for the search box
    search_html = f"""
    <div class="search-container">
        <div class="search-icon">{search_icon}</div>
    </div>
    """
    
    st.markdown(search_html, unsafe_allow_html=True)
    
    # Create the search input
    return st.text_input(
        "Search",
        value=st.session_state.get("search_query", ""),
        placeholder=placeholder,
        key="search_query"
    )


def render_tooltip(content, tooltip_text):
    """Render content with a tooltip.
    
    Args:
        content: The content to display.
        tooltip_text: The text to display in the tooltip.
        
    Returns:
        HTML for the content with a tooltip.
    """
    # Create the HTML for the tooltip
    tooltip_html = f"""
    <div class="tooltip">
        {content}
        <span class="tooltip-text">{tooltip_text}</span>
    </div>
    """
    
    return st.markdown(tooltip_html, unsafe_allow_html=True)


def render_metric_card(label, value, description=""):
    """Render a metric card.
    
    Args:
        label: The label for the metric.
        value: The value of the metric.
        description: A description of the metric.
        
    Returns:
        HTML for the metric card.
    """
    # Create the HTML for the metric card
    metric_html = f"""
    <div class="metric-card">
        <div class="metric-value">{value}</div>
        <div class="metric-label">{label}</div>
        <div class="metric-description">{description}</div>
    </div>
    """
    
    return st.markdown(metric_html, unsafe_allow_html=True)