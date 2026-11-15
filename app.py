import streamlit as st
import pandas as pd
import pydeck as pdk

st.set_page_config(page_title="Delhi Transit Optimizer", page_icon="🚇", layout="centered")

# --- SECURITY MODULE ---
st.title("🔒 Private Access")
passcode = st.text_input("Enter the project passcode to continue:", type="password")

if passcode == "TravelMitra":
    st.success("Access Granted! Welcome.")
    st.divider()
    
    # --- CORE APPLICATION ---
    st.title("🚇 Delhi Transit Optimizer")
    st.markdown("A computational model utilizing Graph Theory and Linear Programming to optimize transit budgets and travel times.")

    delhi_map = {
        "Dwarka Sector 21": {
            "Dwarka Sector 14": {'dist': 1, 'm_change': 0, 'b_change': 0},
            "Palam Village": {'dist': 4, 'm_change': 1, 'b_change': 0},
            "Malviya Nagar / Saket": {'dist': 21, 'm_change': 1, 'b_change': 1},
            "Connaught Place": {'dist': 21, 'm_change': 0, 'b_change': 1}
        },
        "Dwarka Sector 14": {
            "Dwarka Sector 21": {'dist': 1, 'm_change': 0, 'b_change': 0},
            "Palam Village": {'dist': 5, 'm_change': 1, 'b_change': 0},
            "Malviya Nagar / Saket": {'dist': 23, 'm_change': 1, 'b_change': 1},
            "Connaught Place": {'dist': 22, 'm_change': 0, 'b_change': 1}
        },
        "Palam Village": {
            "Dwarka Sector 21": {'dist': 4, 'm_change': 1, 'b_change': 0},
            "Dwarka Sector 14": {'dist': 5, 'm_change': 1, 'b_change': 0},
            "Malviya Nagar / Saket": {'dist': 18, 'm_change': 1, 'b_change': 1},
            "Connaught Place": {'dist': 17, 'm_change': 1, 'b_change': 1}
        },
        "Malviya Nagar / Saket": {
            "Dwarka Sector 21": {'dist': 21, 'm_change': 1, 'b_change': 1},
            "Dwarka Sector 14": {'dist': 23, 'm_change': 1, 'b_change': 1},
            "Palam Village": {'dist': 18, 'm_change': 1, 'b_change': 1},
            "Connaught Place": {'dist': 14, 'm_change': 0, 'b_change': 1}
        },
        "Connaught Place": {
            "Dwarka Sector 21": {'dist': 21, 'm_change': 0, 'b_change': 1},
            "Dwarka Sector 14": {'dist': 22, 'm_change': 0, 'b_change': 1},
            "Palam Village": {'dist': 17, 'm_change': 1, 'b_change': 1},
            "Malviya Nagar / Saket": {'dist': 14, 'm_change': 0, 'b_change': 1}
        }
    }

    locations = list(delhi_map.keys())

    st.subheader("1. Enter Route Details")
    col1, col2 = st.columns(2)
    with col1:
        start_node = st.selectbox("📍 Starting Location", locations)
    with col2:
        end_node = st.selectbox("🏁 Destination", locations, index=1)
        
    col3, col4 = st.columns(2)
    with col3:
        budget = st.number_input("💰 Max Monthly Budget (Rs)", min_value=100.0, value=2000.0, step=100.0)
    with col4:
        work_days = st.number_input("📅 Working Days", min_value=1, value=24, step=1)

    with st.expander("🗺️ View Graph Theory Network (Nodes & Edges)"):
        nodes_df = pd.DataFrame({
            'name
