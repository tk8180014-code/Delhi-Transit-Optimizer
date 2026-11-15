import streamlit as st

st.set_page_config(page_title="Delhi Transit Optimizer", page_icon="🚇", layout="centered")

# --- SECURITY MODULE ---
st.title("🔒 Private Access")
passcode = st.text_input("Enter the project passcode to continue:", type="password")

if passcode == "TravelMitra":
    st.success("Access Granted! Welcome to the project.")
    st.divider()
    
    # --- CORE APPLICATION ---
    st.title("🚇 Delhi Transit Optimizer")
    st.subheader("Smart Route & Budget Planner")

    # GRAPH THEORY: Weighted Adjacency Matrix
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
            "Dwarka Sector 21": {'dist': 21, 'm_change': 0, 'b
