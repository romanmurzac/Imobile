import streamlit as st
import pandas as pd

# Set page configuration.
st.set_page_config(
    page_title="Imobile",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        "Get help": "https://www.linkedin.com/in/roman-murzac/",
        "Report a bug": "https://github.com/romanmurzac/Imobile/issues",
        "About": "Imobile - Evaluation on Romanian Real Estate market: https://github.com/romanmurzac/Imobile",
    },
)

# Main Header.
st.title("Romanian Real Estate Market Insights", text_alignment="center")

# Sidebar Header.
st.sidebar.subheader("Price Evolution")

# Load data.
dim_df = pd.read_parquet("../data/dim/listings.parquet")
mart_df = pd.read_parquet("../data/mart/listings_table.parquet")

# User input.
user_source = st.sidebar.selectbox("Select Source", ["publi"])
user_id = st.sidebar.text_input("Enter ID")

# Data transformations.
history_data = dim_df[(dim_df["source"] == user_source) & (dim_df["id"] == user_id)]

# Display listing details.
st.markdown("### Listing Details")
st.dataframe(
    mart_df,
    column_config={
        "date_posted": st.column_config.DateColumn(
            "Posted Date",
        ),
        "valid_from": st.column_config.DateColumn(
            "Available From",
        ),
        "county": st.column_config.TextColumn(
            "County",
        ),
        "city": st.column_config.TextColumn(
            "City",
        ),
        "address": st.column_config.TextColumn(
            "Address",
        ),
        "price": st.column_config.NumberColumn(
            "Absolut Price (€)",
        ),
        "unit_price": st.column_config.ProgressColumn(
            "Relative Price (€/m²)",
            format="%d",
            min_value=0,
            max_value=4000,
        ),
        "surface": st.column_config.NumberColumn(
            "Surface (m²)",
        ),
        "rooms": st.column_config.NumberColumn(
            "Rooms",
        ),
        "floor": st.column_config.NumberColumn(
            "Floor",
        ),
        "built_year": st.column_config.NumberColumn(
            "Built Year",
        ),
        "is_furnished": st.column_config.CheckboxColumn("Is Furnished?"),
        "near_metro": st.column_config.CheckboxColumn("Near Metro?"),
        "title": st.column_config.TextColumn(
            "Title",
        ),
    },
    hide_index=True,
    width="stretch",
)

# Display price evolution.
st.markdown("### Price Evolution Over Time")
st.bar_chart(history_data, x="date_posted", y="price")
