"""Sidebar component for shared filters across all Streamlit pages."""

import streamlit as st
from src.db import get_species_list
from src.config import DATA_LIMIT_DATE, DEFAULT_START_DATE, DATA_START_DATE

_CSS = """
<style>
/* Hide Streamlit default footer and menu */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* Page title underline */
h1 {
    font-weight: 700;
    padding-bottom: 0.5rem;
    border-bottom: 2px solid #e2e8f0;
    margin-bottom: 1.25rem;
}

/* Metric cards */
[data-testid="stMetric"] {
    background: #f8fafc;
    border: 1px solid #e2e8f0;
    border-radius: 8px;
    padding: 1rem 1.25rem;
}
[data-testid="stMetricLabel"] {
    font-size: 0.8rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    color: #64748b;
}
[data-testid="stMetricValue"] {
    font-size: 1.6rem;
    font-weight: 700;
    color: #0f172a;
}

/* Sidebar */
[data-testid="stSidebar"] {
    border-right: 1px solid #e2e8f0;
}
[data-testid="stSidebar"] h1 {
    border-bottom: none;
    font-size: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: #64748b;
}

/* Buttons */
[data-testid="stButton"] > button {
    border-radius: 6px;
    font-weight: 600;
    padding: 0.4rem 1.2rem;
}

/* Info / success / warning boxes */
[data-testid="stAlert"] {
    border-radius: 6px;
}

/* Expander */
details summary {
    font-weight: 600;
}
</style>
"""


def render_sidebar() -> dict:
    """
    Renders the global sidebar with species and date filters.

    Returns:
        dict: Current filter values {species: str, start_date: date, end_date: date}
    """
    st.markdown(_CSS, unsafe_allow_html=True)
    st.sidebar.title("Filters")

    species_list = get_species_list()

    if "selected_species" not in st.session_state:
        default_species = "Eurasian Blackbird" if "Eurasian Blackbird" in species_list else species_list[0]
        st.session_state.selected_species = default_species

    selected_species = st.sidebar.selectbox(
        "Select Species",
        options=species_list,
        index=species_list.index(st.session_state.selected_species) if st.session_state.selected_species in species_list else 0,
        key="species_selectbox"
    )
    st.session_state.selected_species = selected_species

    st.sidebar.subheader("Date Range")

    if "date_range" not in st.session_state:
        st.session_state.date_range = (DEFAULT_START_DATE, DATA_LIMIT_DATE)

    date_range = st.sidebar.date_input(
        "Select Range",
        value=st.session_state.date_range,
        min_value=DATA_START_DATE,
        max_value=DATA_LIMIT_DATE,
        key="date_range_input"
    )

    if isinstance(date_range, (tuple, list)) and len(date_range) == 2:
        start, end = date_range[0], date_range[1]
        st.session_state.date_range = (start, end)

    if not isinstance(st.session_state.date_range, (tuple, list)) or len(st.session_state.date_range) != 2:
        st.session_state.date_range = (DEFAULT_START_DATE, DATA_LIMIT_DATE)

    return {
        "species": st.session_state.selected_species,
        "start_date": st.session_state.date_range[0],
        "end_date": st.session_state.date_range[1]
    }
