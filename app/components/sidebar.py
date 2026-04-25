"""Sidebar component for shared filters across all Streamlit pages."""

import streamlit as st
from datetime import date
from src.db import get_species_list

def render_sidebar() -> dict:
    """
    Renders the global sidebar with species and date filters.
    
    Returns:
        dict: Current filter values {species: str, start_date: date, end_date: date}
    """
    st.sidebar.title("Global Filters")
    
    # Species filter
    species_list = get_species_list()
    
    # Initialize session state if needed
    if "selected_species" not in st.session_state:
        # Default to Eurasian Blackbird if available, else first in list
        default_species = "Eurasian Blackbird" if "Eurasian Blackbird" in species_list else species_list[0]
        st.session_state.selected_species = default_species
        
    selected_species = st.sidebar.selectbox(
        "Select Species",
        options=species_list,
        index=species_list.index(st.session_state.selected_species) if st.session_state.selected_species in species_list else 0,
        key="species_selectbox"
    )
    st.session_state.selected_species = selected_species
    
    # Date range filter
    st.sidebar.subheader("Date Range")
    
    if "date_range" not in st.session_state:
        st.session_state.date_range = (date(2023, 1, 1), date(2023, 12, 31))
        
    date_range = st.sidebar.date_input(
        "Select Range",
        value=st.session_state.date_range,
        min_value=date(2015, 1, 1),
        max_value=date(2024, 12, 31),
        key="date_range_input"
    )
    
    # Handle both single date and range (streamlit date_input returns a tuple for range)
    if isinstance(date_range, tuple) and len(date_range) == 2:
        st.session_state.date_range = date_range
    elif isinstance(date_range, date):
        # If user only clicked one date so far, we keep it as a range from that date to itself
        # though usually it's a tuple.
        pass

    return {
        "species": st.session_state.selected_species,
        "start_date": st.session_state.date_range[0],
        "end_date": st.session_state.date_range[1]
    }
