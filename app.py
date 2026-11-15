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
        budget = st.number_input("💰 Max Budget (Rs)", min_value=10.0, value=2000.0, step=50.0)
    with col4:
        total_trips = st.number_input("📅 Total Trips Needed", min_value=1, value=48, step=1)

    with st.expander("🗺️ View Graph Theory Network (Nodes & Edges)"):
        nodes_df = pd.DataFrame({
            'name': locations,
            'lat': [28.5523, 28.6024, 28.5844, 28.5290, 28.6304],
            'lon': [77.0583, 77.0256, 77.0805, 77.2052, 77.2177]
        })
        
        edges = []
        for i in range(len(locations)):
            for j in range(i + 1, len(locations)):
                edges.append({
                    "source_lat": nodes_df.iloc[i]['lat'],
                    "source_lon": nodes_df.iloc[i]['lon'],
                    "target_lat": nodes_df.iloc[j]['lat'],
                    "target_lon": nodes_df.iloc[j]['lon']
                })
        edges_df = pd.DataFrame(edges)

        view_state = pdk.ViewState(latitude=28.5800, longitude=77.1200, zoom=10, pitch=40)
        
        scatter_layer = pdk.Layer(
            "ScatterplotLayer",
            data=nodes_df,
            get_position="[lon, lat]",
            get_color="[255, 50, 50, 200]",
            get_radius=1200,
        )
        
        line_layer = pdk.Layer(
            "LineLayer",
            data=edges_df,
            get_source_position="[source_lon, source_lat]",
            get_target_position="[target_lon, target_lat]",
            get_color="[100, 150, 250, 150]",
            get_width=3,
        )

        st.pydeck_chart(pdk.Deck(layers=[line_layer, scatter_layer], initial_view_state=view_state))

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
                
                min_trips = total_trips
                interchange_penalty = 3 
                
                metro_time = ((distance / 40) * 60) + (metro_changes * (5 + interchange_penalty)) + 15
                bus_time = ((distance / 15) * 60) + (bus_changes * (2 + interchange_penalty)) + 15
                
                # Minimum Rs 10 fare logic implemented here
                metro_fare = max(10, min((distance * 2), 60)) + (metro_changes * 40)
                bus_fare = max(10, min((distance * 1), 25)) + (bus_changes * 15)
                
                # --- Unconstrained Extreme Scenarios ---
                # Fastest Scenario (Ignore Budget)
                fastest_mode_time = min(metro_time, bus_time)
                fastest_cost = (metro_fare if metro_time < bus_time else bus_fare) * min_trips
                fastest_total_time = fastest_mode_time * min_trips
                
                # Cheapest Scenario (Ignore Time)
                cheapest_mode_fare = min(metro_fare, bus_fare)
                cheapest_total_cost = cheapest_mode_fare * min_trips
                cheapest_total_time = (metro_time if metro_fare < bus_fare else bus_time) * min_trips
                
                # --- Integer LP Loop (Your Optimal Budget) ---
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
                    
                    # Converted to Time Per Trip
                    time_per_trip = best_time / min_trips
                    m3.metric(label="Avg Time Per Trip", value=f"{round(time_per_trip)} mins")
                    
                    savings = budget - best_cost
                    m4, m5 = st.columns(2)
                    m4.metric(label="Total Projected Cost", value=f"Rs {round(best_cost)}")
                    m5.metric(label="Capital Saved", value=f"Rs {round(savings)}")
                    
                    # BUDGET VISUALIZATION BAR
                    budget_pct = best_cost / budget
                    st.progress(min(budget_pct, 1.0))
                    st.caption(f"**Budget Consumed:** {round(budget_pct * 100)}%")
                    
                    st.caption(f"*One-way time breakdown (including last-mile): Metro ~{round(metro_time)} mins, Bus ~{round(bus_time)} mins*")
                    st.caption(f"*One-way fare breakdown: Metro Rs {round(metro_fare)}, Bus Rs {round(bus_fare)}*")
                    
                    # ANALYTICS COMPARISON CHART
                    st.divider()
                    st.subheader("📊 Scenario Analytics")
                    st.markdown("Comparing your budget-optimized plan against the extreme fastest and cheapest mathematical paths.")
                    
                    # Chart now displays Time Per Trip instead of total monthly time
                    chart_data = pd.DataFrame({
                        "Total Cost (Rs)": [fastest_cost, best_cost, cheapest_total_cost],
                        "Time Per Trip (Mins)": [fastest_mode_time, time_per_trip, (cheapest_total_time / min_trips)]
                    }, index=["Fastest Path (No Budget)", "Your Optimal Plan", "Cheapest Path (Max Time)"])
                    
                    st.bar_chart(chart_data)
                    
                else:
                    min_required_budget = min_trips * min_possible_fare
                    st.error(f"Rs {round(budget)} is insufficient for this route.")
                    st.write(f"The absolute minimum capital required is **Rs {round(min_required_budget)}**.")
                    st.write(f"Please increase the budget by **Rs {round(min_required_budget - budget)}** and recalculate.")
