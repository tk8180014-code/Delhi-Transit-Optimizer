import streamlit as st
import pandas as pd

# Reverted to a centered, clean layout
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

    # UI: Clean, centered input columns
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

    # UI: Map hidden in a sleek dropdown to keep the screen uncluttered
    with st.expander("🗺️ View Delhi Network Nodes"):
        map_data = pd.DataFrame({
            'lat': [28.5523, 28.6024, 28.5844, 28.5290, 28.6304],
            'lon': [77.0583, 77.0256, 77.0805, 77.2052, 77.2177],
            'name': locations
        })
        st.map(map_data, zoom=10, use_container_width=True)

    # Core Execution
    if st.button("🚀 Calculate Optimal Route", use_container_width=True, type="primary"):
        if start_node == end_node:
            st.warning("You are already at your destination!")
        else:
            with st.spinner('Calculating Linear Programming Constraints...'):
                
                route_data = delhi_map[start_node][end_node]
                distance = route_data['dist']
                metro_changes = route_data['m_change']
                bus_changes = route_data['b_change']
                
                st.info(f"**Network Snapshot:** {distance} km | Metro Interchanges: {metro_changes} | Bus Interchanges: {bus_changes}")
                
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
                st.subheader("2. Optimal Allocation Results")

                if best_time != float('inf'):
                    m1, m2, m3 = st.columns(3)
                    m1.metric(label="Metro Allocations", value=best_metro)
                    m2.metric(label="Bus Allocations", value=best_bus)
                    
                    daily_avg_time = best_time / work_days
                    m3.metric(label="Daily Commute Time", value=f"{round(daily_avg_time)} mins")
                    
                    savings = budget - best_cost
                    
                    m4, m5 = st.columns(2)
                    m4.metric(label="Total Projected Cost", value=f"Rs {round(best_cost)}")
                    m5.metric(label="Capital Saved", value=f"Rs {round(savings)}")
                    
                    st.caption(f"*One-way time breakdown (including last-mile): Metro ~{round(metro_time)} mins, Bus ~{round(bus_time)} mins*")
                    st.caption(f"*One-way fare breakdown: Metro Rs {round(metro_fare)}, Bus Rs {round(bus_fare)}*")
                    st.caption(f"*(Note: An estimated wait penalty of 3 minutes is automatically factored in per interchange.)*")
                else:
                    min_required_budget = min_trips * min_possible_fare
                    st.error(f"Rs {round(budget)} is insufficient for this route.")
                    st.write(f"The absolute minimum capital required is **Rs {round(min_required_budget)}**.")
                    st.write(f"Please increase the budget by **Rs {round(min_required_budget - budget)}** and recalculate.")
