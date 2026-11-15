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

    # GRAPH THEORY: Weighted Adjacency Matrix (Updated Locations)
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

    # UI: Input Fields
    col1, col2 = st.columns(2)
    with col1:
        start_node = st.selectbox("Starting Location", locations)
    with col2:
        end_node = st.selectbox("Destination", locations, index=1)

    col3, col4, col5 = st.columns(3)
    with col3:
        budget = st.number_input("Maximum Monthly Budget (Rs)", min_value=100.0, value=2000.0, step=100.0)
    with col4:
        work_days = st.number_input("Working Days", min_value=1, value=24, step=1)
    with col5:
        time_of_day = st.selectbox("Traffic Factor", ["Off-Peak (Normal)", "Peak Rush Hour"])

    if st.button("Optimize My Route", use_container_width=True, type="primary"):
        if start_node == end_node:
            st.warning("You are already at your destination!")
        else:
            # Data Extraction
            route_data = delhi_map[start_node][end_node]
            distance = route_data['dist']
            metro_changes = route_data['m_change']
            bus_changes = route_data['b_change']
            
            st.info(f"**Route Snapshot:** {distance} km | Metro Changes: {metro_changes} | Bus Changes: {bus_changes}")
            
            min_trips = work_days * 2
            
            # --- REAL-WORLD TIME ABSTRACTION ---
            # Dynamic Wait Penalty Logic
            if time_of_day == "Peak Rush Hour":
                metro_wait_penalty = 8  # Heavy crowd delay
                bus_wait_penalty = 20   # Traffic jams
            else:
                metro_wait_penalty = 3  # Normal wait
                bus_wait_penalty = 8    # Normal wait
                
            # Base Time Calculation (Speed + Transfer Walking + Wait Penalty)
            metro_time = ((distance / 40) * 60) + (metro_changes * (5 + metro_wait_penalty))
            bus_time = ((distance / 15) * 60) + (bus_changes * (2 + bus_wait_penalty))
            
            # First & Last Mile Factor (Walking/Auto from home to the actual station)
            first_last_mile_penalty = 15 
            metro_time += first_last_mile_penalty
            bus_time += first_last_mile_penalty
            
            # Financial Abstraction
            metro_fare = min((distance * 2), 60) + (metro_changes * 40)
            bus_fare = min((distance * 1), 25) + (bus_changes * 15)
            
            # --- INTEGER LINEAR PROGRAMMING LOOP ---
            best_time = float('inf')
            best_cost = float('inf')
            best_metro = 0
            best_bus = 0
            
            min_possible_fare = min(metro_fare, bus_fare)
            max_trips = int((budget // min_possible_fare) + 1)
            
            for metro_trips in range(max_trips):
                for bus_trips in range(max_trips):
                    current_cost = (metro_fare * metro_trips) + (bus_fare * bus_trips)
                    
                    # Core Constraints: Total trips must meet monthly requirement, and Cost must stay under budget
                    if (metro_trips + bus_trips >= min_trips) and (current_cost <= budget):
                        total_time = (metro_time * metro_trips) + (bus_time * bus_trips)
                        
                        # Optimization Logic: Prioritize lowest time. If times are identical, prioritize lowest cost.
                        if total_time < best_time or (total_time == best_time and current_cost < best_cost):
                            best_time = total_time
                            best_cost = current_cost
                            best_metro = metro_trips
                            best_bus = bus_trips

            # --- UI OUTPUTS ---
            st.divider()
            st.subheader("Your Optimal Monthly Plan")

            if best_time != float('inf'):
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
                
                st.success("Optimization Complete! Enjoy your ride.")
            else:
                min_required_budget = min_trips * min_possible_fare
                st.error(f"Rs {round(budget)} is too low for this route.")
                st.write(f"You need an absolute minimum of **Rs {round(min_required_budget)}** to commute this month.")
                st.write(f"Add **Rs {round(min_required_budget - budget)}** to your budget and calculate again.")
