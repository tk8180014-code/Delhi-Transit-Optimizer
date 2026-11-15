import streamlit as st
import pandas as pd
import time

# Changed layout to "wide" for a more professional dashboard look
st.set_page_config(page_title="Delhi Transit Optimizer", page_icon="🚇", layout="wide")

# --- SECURITY MODULE ---
st.title("🔒 Private Access")
passcode = st.text_input("Enter the project passcode to continue:", type="password")

if passcode == "TravelMitra":
    st.success("Access Granted! Welcome to the project.")
    st.divider()
    
    # --- CORE APPLICATION ---
    # UI: Move inputs to a professional Sidebar
    st.sidebar.title("⚙️ Mission Control")
    st.sidebar.subheader("Transit Parameters")

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

    start_node = st.sidebar.selectbox("📍 Starting Location", locations)
    end_node = st.sidebar.selectbox("🏁 Destination", locations, index=1)
    
    st.sidebar.divider()
    budget = st.sidebar.number_input("💰 Max Monthly Budget (Rs)", min_value=100.0, value=2000.0, step=100.0)
    work_days = st.sidebar.number_input("📅 Working Days", min_value=1, value=24, step=1)

    # Main Screen Title
    st.title("🚇 Delhi Transit Optimizer")
    st.markdown("### Graph Theory & LP Routing Engine")

    # Map Visualizer Data
    map_data = pd.DataFrame({
        'lat': [28.5523, 28.6024, 28.5844, 28.5290, 28.6304],
        'lon': [77.0583, 77.0256, 77.0805, 77.2052, 77.2177],
        'name': locations
    })

    # Render the interactive map on the main screen
    st.map(map_data, zoom=10, use_container_width=True)

    if st.sidebar.button("🚀 Optimize My Route", use_container_width=True, type="primary"):
        if start_node == end_node:
            st.warning("You are already at your destination!")
        else:
            # Cinematic Loading Animation
            with st.spinner('Running Integer Linear Programming Loop...'):
                time.sleep(1.5)  # Fake delay for visual effect
                
            # Data Extraction
            route_data = delhi_map[start_node][end_node]
            distance = route_data['dist']
            metro_changes = route_data['m_change']
            bus_changes = route_data['b_change']
            
            st.info(f"**Route Snapshot:** {distance} km | Metro Changes: {metro_changes} | Bus Changes: {bus_changes}")
            
            min_trips = work_days * 2
            interchange_penalty = 3 
            
            metro_time = ((distance / 40) * 60) + (metro_changes * (5 + interchange_penalty)) + 15
            bus_time = ((distance / 15) * 60) + (bus_changes * (2 + interchange_penalty)) + 15
            
            metro_fare = min((distance * 2), 60) + (metro_changes * 40)
            bus_fare = min((distance * 1), 25) + (bus_changes * 15)
            
            best_time = float('inf')
            best_cost = float('inf')
            best_metro = 0
            best_bus = 0
            
            min_possible_fare = min(metro_fare, bus_fare)
            max_trips = int((budget // min_possible_fare) + 1)
            
            for metro_trips in range(max_trips):
                for bus_trips in range(max_trips):
                    current_cost = (metro_fare * metro_trips) + (bus_fare * bus_trips)
                    if (metro_trips + bus_trips >= min_trips) and (current_cost <= budget):
                        total_time = (metro_time * metro_trips) + (bus_time * bus_trips)
                        if total_time < best_time or (total_time == best_time and current_cost < best_cost):
                            best_time = total_time
                            best_cost = current_cost
                            best_metro = metro_trips
                            best_bus = bus_trips

            st.divider()
            st.subheader("✅ Your Optimal Monthly Plan")

            if best_time != float('inf'):
                st.balloons() # Triggers the visual Easter egg
                
                m1, m2, m3 = st.columns(3)
                m1.metric(label="Metro Trips", value=best_metro)
                m2.metric(label="Bus Trips", value=best_bus)
                
                daily_avg_time = best_time / work_days
                m3.metric(label="Daily Commute Time", value=f"{round(daily_avg_time)} mins")
                
                savings = budget - best_cost
                
                m4, m5 = st.columns(2)
                m4.metric(label="Total Money Spent", value=f"Rs {round(best_cost)}")
                m5.metric(label="Money Saved", value=f"Rs {round(savings)}")
                
                st.caption(f"*One-way time breakdown (including last-mile): Metro ~{round(metro_time)} mins, Bus ~{round(bus_time)} mins*")
                st.caption(f"*One-way fare breakdown: Metro Rs {round(metro_fare)}, Bus Rs {round(bus_fare)}*")
                st.caption(f"*(Note: An estimated wait penalty of 1-5 minutes is automatically factored in per interchange.)*")
            else:
                min_required_budget = min_trips * min_possible_fare
                st.error(f"Rs {round(budget)} is too low for this route.")
                st.write(f"You need an absolute minimum of **Rs {round(min_required_budget)}** to commute this month.")
                st.write(f"Add **Rs {round(min_required_budget - budget)}** to your budget and calculate again.")
