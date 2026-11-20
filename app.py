import heapq
import math
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import pydeck as pdk
import streamlit as st

# ==========================================
# 1. PAGE CONFIG
# ==========================================
st.set_page_config(
    page_title="Travel Mitra 2.0 | Delhi Transit Optimizer",
    page_icon="🚇",
    layout="wide",
)

# ==========================================
# 2. REAL DELHI TRANSIT GRAPH (LAT, LON)
# ==========================================
NODES = {
    "Dwarka Sector 21": (28.5522, 77.0583),
    "Dwarka Sector 14": (28.6022, 77.0258),
    "Palam Village": (28.5892, 77.0844),
    "Janakpuri West": (28.6295, 77.0777),
    "Rajouri Garden": (28.6492, 77.1219),
    "Dhaula Kuan": (28.5919, 77.1616),
    "Connaught Place (Rajiv Chowk)": (28.6328, 77.2197),
    "AIIMS": (28.5672, 77.2100),
    "Hauz Khas": (28.5433, 77.2066),
    "Malviya Nagar": (28.5286, 77.2063),
    "Saket": (28.5206, 77.2015),
    "Nehru Place": (28.5491, 77.2513),
}

# Bidirectional edges: (Node A, Node B, Distance_km, Mode)
EDGES = [
    # --- METRO LINES (Blue, Magenta, Yellow, Airport Exp) ---
    ("Dwarka Sector 21", "Dwarka Sector 14", 6.5, "Metro"),
    ("Dwarka Sector 14", "Janakpuri West", 6.2, "Metro"),
    ("Janakpuri West", "Rajouri Garden", 5.4, "Metro"),
    ("Rajouri Garden", "Connaught Place (Rajiv Chowk)", 11.2, "Metro"),
    ("Dwarka Sector 21", "Dhaula Kuan", 12.8, "Metro"),
    ("Dhaula Kuan", "Connaught Place (Rajiv Chowk)", 8.5, "Metro"),
    ("Janakpuri West", "Palam Village", 4.8, "Metro"),
    ("Palam Village", "Hauz Khas", 13.5, "Metro"),
    ("Hauz Khas", "Nehru Place", 5.2, "Metro"),
    ("Connaught Place (Rajiv Chowk)", "AIIMS", 7.8, "Metro"),
    ("AIIMS", "Hauz Khas", 3.2, "Metro"),
    ("Hauz Khas", "Malviya Nagar", 2.1, "Metro"),
    ("Malviya Nagar", "Saket", 1.5, "Metro"),

    # --- DTC BUS ROUTES (Road Network) ---
    ("Dwarka Sector 21", "Dwarka Sector 14", 7.2, "Bus"),
    ("Dwarka Sector 21", "Palam Village", 5.5, "Bus"),
    ("Dwarka Sector 14", "Palam Village", 6.4, "Bus"),
    ("Dwarka Sector 14", "Janakpuri West", 6.8, "Bus"),
    ("Palam Village", "Janakpuri West", 5.2, "Bus"),
    ("Palam Village", "Dhaula Kuan", 9.4, "Bus"),
    ("Janakpuri West", "Rajouri Garden", 5.8, "Bus"),
    ("Rajouri Garden", "Dhaula Kuan", 8.0, "Bus"),
    ("Rajouri Garden", "Connaught Place (Rajiv Chowk)", 12.1, "Bus"),
    ("Dhaula Kuan", "Connaught Place (Rajiv Chowk)", 9.2, "Bus"),
    ("Dhaula Kuan", "AIIMS", 6.8, "Bus"),
    ("Dhaula Kuan", "Hauz Khas", 8.5, "Bus"),
    ("Connaught Place (Rajiv Chowk)", "AIIMS", 8.4, "Bus"),
    ("AIIMS", "Hauz Khas", 3.6, "Bus"),
    ("AIIMS", "Nehru Place", 6.5, "Bus"),
    ("Hauz Khas", "Malviya Nagar", 2.5, "Bus"),
    ("Hauz Khas", "Nehru Place", 5.8, "Bus"),
    ("Malviya Nagar", "Saket", 1.8, "Bus"),
    ("Malviya Nagar", "Nehru Place", 5.4, "Bus"),
    ("Saket", "Nehru Place", 6.2, "Bus"),

    # --- FIRST / LAST MILE (E-Rickshaw / Auto Feeder) ---
    ("Dwarka Sector 21", "Palam Village", 5.0, "E-Rickshaw"),
    ("Dwarka Sector 14", "Palam Village", 5.8, "E-Rickshaw"),
    ("Hauz Khas", "Malviya Nagar", 2.2, "E-Rickshaw"),
    ("Malviya Nagar", "Saket", 1.6, "E-Rickshaw"),
]

# Speeds in km/h (Peak vs Off-Peak)
SPEEDS = {
    "Off-Peak": {"Metro": 40.0, "Bus": 18.0, "E-Rickshaw": 15.0},
    "Peak (Rush Hour)": {"Metro": 37.0, "Bus": 11.0, "E-Rickshaw": 10.0},
}

INTERCHANGE_PENALTY_MIN = 4.0  # Minutes lost when switching modes

DTC_PASSES = {
    "None (Pay-per-trip)": 0,
    "DTC Student Pass (₹100/mo)": 100,
    "DTC Non-AC Pass (₹800/mo)": 800,
    "DTC AC Pass (₹1000/mo)": 1000,
}


# ==========================================
# 3. FARE & GRAPH ENGINE (DIJKSTRA)
# ==========================================
def calc_dmrc_fare(distance_km: float, smart_card: bool, is_off_peak: bool) -> float:
    if distance_km <= 0:
        return 0.0
    if distance_km <= 2:
        base = 10.0
    elif distance_km <= 5:
        base = 20.0
    elif distance_km <= 12:
        base = 30.0
    elif distance_km <= 21:
        base = 40.0
    elif distance_km <= 32:
        base = 50.0
    else:
        base = 60.0

    if smart_card:
        base *= 0.90  # 10% Smart Card discount
        if is_off_peak:
            base *= 0.90  # Additional 10% off-peak discount
    return round(base, 1)


def calc_bus_fare(distance_km: float, ac_bus: bool = False) -> float:
    if distance_km <= 0:
        return 0.0
    if ac_bus:
        if distance_km <= 4:
            return 10.0
        elif distance_km <= 10:
            return 15.0
        return 25.0
    else:
        if distance_km <= 4:
            return 5.0
        elif distance_km <= 10:
            return 10.0
        return 15.0


def calc_erickshaw_fare(distance_km: float) -> float:
    if distance_km <= 0:
        return 0.0
    return 10.0 if distance_km <= 3 else 20.0


def build_adjacency_list(allowed_modes: set):
    adj = {node: [] for node in NODES}
    for u, v, dist, mode in EDGES:
        if mode in allowed_modes:
            adj[u].append((v, dist, mode))
            adj[v].append((u, dist, mode))
    return adj


def dijkstra_multimodal(
    origin: str,
    destination: str,
    allowed_modes: set,
    traffic_period: str,
    smart_card: bool,
    ac_bus: bool,
):
    """
    Finds shortest-time path using Dijkstra's algorithm with mode-switch penalties.
    Returns dict with path, segments, total_time, total_dist, and cost breakdown.
    """
    adj = build_adjacency_list(allowed_modes)
    speeds = SPEEDS[traffic_period]
    is_off_peak = traffic_period == "Off-Peak"

    # Priority queue: (cum_time, current_node, prev_mode, path_segments)
    pq = [(0.0, origin, None, [])]
    visited = {}  # (node, mode) -> best_time

    while pq:
        cum_time, node, prev_mode, segments = heapq.heappop(pq)

        if node == destination:
            metro_km = sum(s["dist"] for s in segments if s["mode"] == "Metro")
            bus_km = sum(s["dist"] for s in segments if s["mode"] == "Bus")
            erick_km = sum(s["dist"] for s in segments if s["mode"] == "E-Rickshaw")

            metro_cost = calc_dmrc_fare(metro_km, smart_card, is_off_peak)
            bus_cost = calc_bus_fare(bus_km, ac_bus=ac_bus)
            erick_cost = calc_erickshaw_fare(erick_km)

            return {
                "time_min": round(cum_time, 1),
                "dist_km": round(metro_km + bus_km + erick_km, 1),
                "metro_cost": metro_cost,
                "bus_cost": bus_cost,
                "erick_cost": erick_cost,
                "total_cost": round(metro_cost + bus_cost + erick_cost, 1),
                "segments": segments,
            }

        state = (node, prev_mode)
        if state in visited and visited[state] <= cum_time:
            continue
        visited[state] = cum_time

        for nxt, dist, mode in adj[node]:
            travel_time = (dist / speeds[mode]) * 60.0
            penalty = INTERCHANGE_PENALTY_MIN if (prev_mode and prev_mode != mode) else 0.0
            new_time = cum_time + travel_time + penalty
            new_seg = segments + [
                {"from": node, "to": nxt, "dist": dist, "mode": mode, "time": round(travel_time, 1)}
            ]
            heapq.heappush(pq, (new_time, nxt, mode, new_seg))

    return None


# ==========================================
# 4. INTEGER LINEAR PROGRAMMING + PASS SOLVER
# ==========================================
def solve_monthly_ilp(
    fast_route: dict,
    budget_route: dict,
    total_trips: int,
    max_budget: float,
    allowed_passes: list,
):
    """
    Minimizes Total Monthly Time: T_fast * x + T_budget * y
    Subject to:
        x + y = total_trips  (x, y >= 0, integers)
        Pass_Cost + C_fast(pass) * x + C_budget(pass) * y <= max_budget
    Evaluates all allowed pass options to find the global optimum.
    """
    best_solution = None
    min_feasible_cost = float("inf")

    for pass_name in allowed_passes:
        pass_fixed_cost = DTC_PASSES[pass_name]
        bus_covered = pass_name != "None (Pay-per-trip)"

        # If a DTC pass is active, bus fare component drops to ₹0 per trip
        c_fast = fast_route["metro_cost"] + fast_route["erick_cost"] + (0 if bus_covered else fast_route["bus_cost"])
        c_budget = budget_route["metro_cost"] + budget_route["erick_cost"] + (0 if bus_covered else budget_route["bus_cost"])

        t_fast = fast_route["time_min"]
        t_budget = budget_route["time_min"]

        for x in range(total_trips + 1):
            y = total_trips - x
            total_cost = round(pass_fixed_cost + (c_fast * x) + (c_budget * y), 1)
            total_time = round((t_fast * x) + (t_budget * y), 1)

            if total_cost < min_feasible_cost:
                min_feasible_cost = total_cost

            if total_cost <= max_budget:
                if (
                    best_solution is None
                    or total_time < best_solution["total_time_min"]
                    or (total_time == best_solution["total_time_min"] and total_cost < best_solution["total_cost"])
                ):
                    best_solution = {
                        "x_fast": x,
                        "y_budget": y,
                        "pass_used": pass_name,
                        "pass_cost": pass_fixed_cost,
                        "total_cost": total_cost,
                        "total_time_min": total_time,
                        "total_time_hrs": round(total_time / 60.0, 2),
                    }

    return best_solution, round(min_feasible_cost, 1)


def compute_pareto_frontier(fast_route, budget_route, total_trips, allowed_passes):
    """Generates non-dominated (Cost, Time) points across the feasible budget spectrum."""
    _, min_cost = solve_monthly_ilp(fast_route, budget_route, total_trips, float("inf"), allowed_passes)
    max_needed = max(
        fast_route["total_cost"] * total_trips,
        budget_route["total_cost"] * total_trips,
        min_cost + 500,
    )

    budgets = np.linspace(min_cost, max_needed, 60)
    points = []
    seen = set()

    for b in budgets:
        sol, _ = solve_monthly_ilp(fast_route, budget_route, total_trips, float(b), allowed_passes)
        if sol:
            key = (sol["total_cost"], sol["total_time_hrs"])
            if key not in seen:
                seen.add(key)
                points.append(sol)

    df = pd.DataFrame(points).sort_values("total_cost").reset_index(drop=True)
    # Filter to strictly Pareto-optimal points (as cost increases, time must strictly decrease)
    pareto_rows = []
    best_time = float("inf")
    for _, row in df.iterrows():
        if row["total_time_hrs"] < best_time:
            best_time = row["total_time_hrs"]
            pareto_rows.append(row)
    return pd.DataFrame(pareto_rows)


# ==========================================
# 5. SIDEBAR CONTROLS
# ==========================================
st.sidebar.title("⚙️ Commute Parameters")

node_list = list(NODES.keys())
origin = st.sidebar.selectbox("Origin", node_list, index=0)
destination = st.sidebar.selectbox("Destination", node_list, index=6)

st.sidebar.markdown("---")
total_trips = st.sidebar.slider("Monthly Trips (One-Way)", min_value=10, max_value=80, value=44, step=2)
monthly_budget = st.sidebar.slider("Monthly Budget (₹)", min_value=200, max_value=4000, value=1400, step=50)
traffic_period = st.sidebar.radio("Traffic Condition", ["Peak (Rush Hour)", "Off-Peak"])

st.sidebar.markdown("---")
st.sidebar.subheader("Commuter Economics")
smart_card = st.sidebar.checkbox("DMRC Smart Card (10% off + Off-Peak)", value=True)
ac_bus = st.sidebar.checkbox("Prefer AC DTC Buses", value=False)
student_eligible = st.sidebar.checkbox("Eligible for DTC Student Pass (₹100/mo)", value=False)

allowed_passes = ["None (Pay-per-trip)", "DTC AC Pass (₹1000/mo)" if ac_bus else "DTC Non-AC Pass (₹800/mo)"]
if student_eligible:
    allowed_passes.append("DTC Student Pass (₹100/mo)")

# ==========================================
# 6. MAIN DASHBOARD
# ==========================================
st.title("🚇 Travel Mitra 2.0 — Delhi Multi-Modal Transit Optimizer")
st.caption("Graph Theory (Multi-Modal Dijkstra) + Integer Linear Programming (Pass Break-Even & Pareto Optimization)")

if origin == destination:
    st.warning("Origin and Destination cannot be the same. Select two different locations in the sidebar.")
    st.stop()

# Compute Fastest (All Modes) and Budget (Bus + E-Rickshaw) routes
fast_route = dijkstra_multimodal(
    origin, destination, {"Metro", "Bus", "E-Rickshaw"}, traffic_period, smart_card, ac_bus
)
budget_route = dijkstra_multimodal(
    origin, destination, {"Bus", "E-Rickshaw"}, traffic_period, smart_card, ac_bus
)

solution, min_capital = solve_monthly_ilp(fast_route, budget_route, total_trips, monthly_budget, allowed_passes)

# Top Route Comparison Cards
col_a, col_b = st.columns(2)
with col_a:
    st.info(
        f"**Fastest Multi-Modal Route:** {fast_route['time_min']} min | ₹{fast_route['total_cost']} / trip | {fast_route['dist_km']} km"
    )
with col_b:
    st.success(
        f"**Budget Road Route (Bus/E-Rickshaw):** {budget_route['time_min']} min | ₹{budget_route['total_cost']} / trip | {budget_route['dist_km']} km"
    )

# ILP Verdict
if solution is None:
    st.error(
        f"**Infeasible Solution:** Your budget of ₹{monthly_budget} cannot cover {total_trips} trips. "
        f"Minimum capital required is **₹{min_capital}**."
    )
else:
    all_bus_time = (budget_route["time_min"] * total_trips) / 60.0
    hours_saved = round(all_bus_time - solution["total_time_hrs"], 1)

    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Optimal Trip Split", f"{solution['x_fast']} Fast / {solution['y_budget']} Budget")
    m2.metric("Total Monthly Time", f"{solution['total_time_hrs']} hrs", f"-{hours_saved} hrs vs all-bus")
    m3.metric("Total Monthly Spend", f"₹{solution['total_cost']}", f"₹{round(monthly_budget - solution['total_cost'], 1)} left")
    m4.metric("Best Pass Strategy", solution["pass_used"].split(" (")[0])

# ==========================================
# 7. INTERACTIVE DELHI MAP (PYDECK) + PARETO FRONTIER
# ==========================================
st.markdown("---")
map_col, chart_col = st.columns([1.2, 1])

with map_col:
    st.subheader("🗺️ Interactive Delhi Transit Network")

    def route_to_path(segments):
        coords = []
        for idx, s in enumerate(segments):
            lat1, lon1 = NODES[s["from"]]
            lat2, lon2 = NODES[s["to"]]
            if idx == 0:
                coords.append([lon1, lat1])
            coords.append([lon2, lat2])
        return coords

    path_data = [
        {"name": "Budget Route (Bus/E-Rickshaw)", "path": route_to_path(budget_route["segments"]), "color": [255, 165, 0, 200]},
        {"name": "Fastest Multi-Modal Route", "path": route_to_path(fast_route["segments"]), "color": [0, 200, 140, 240]},
    ]

    node_df = pd.DataFrame(
        [
            {
                "name": name,
                "lat": lat,
                "lon": lon,
                "color": [255, 60, 60, 240] if name in (origin, destination) else [200, 200, 200, 180],
                "radius": 450 if name in (origin, destination) else 250,
            }
            for name, (lat, lon) in NODES.items()
        ]
    )

    path_layer = pdk.Layer(
        "PathLayer",
        data=path_data,
        get_path="path",
        get_color="color",
        width_scale=20,
        width_min_pixels=4,
        pickable=True,
    )

    scatter_layer = pdk.Layer(
        "ScatterplotLayer",
        data=node_df,
        get_position="[lon, lat]",
        get_fill_color="color",
        get_radius="radius",
        pickable=True,
    )

    view_state = pdk.ViewState(latitude=28.585, longitude=77.14, zoom=10.8, pitch=30)
    st.pydeck_chart(
        pdk.Deck(
            layers=[path_layer, scatter_layer],
            initial_view_state=view_state,
            tooltip={"text": "{name}"},
        )
    )
    st.caption("🟢 Emerald = Fastest Multi-Modal Route | 🟠 Orange = Budget Road Route | 🔴 Red = Origin / Destination")

with chart_col:
    st.subheader("📈 Pareto Frontier (Cost vs. Time)")
    pareto_df = compute_pareto_frontier(fast_route, budget_route, total_trips, allowed_passes)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=pareto_df["total_cost"],
            y=pareto_df["total_time_hrs"],
            mode="lines+markers",
            name="Pareto Optimal Frontier",
            line=dict(color="#00C88C", width=3),
            hovertemplate="Spend: ₹%{x}<br>Time: %{y} hrs<extra></extra>",
        )
    )

    if solution:
        fig.add_trace(
            go.Scatter(
                x=[solution["total_cost"]],
                y=[solution["total_time_hrs"]],
                mode="markers",
                name="Your Current Plan",
                marker=dict(color="#FF4B4B", size=14, symbol="star"),
            )
        )

    fig.update_layout(
        xaxis_title="Monthly Spend (₹)",
        yaxis_title="Total Monthly Commute Time (Hours)",
        height=420,
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    # Marginal trade-off insight
    if solution and not pareto_df.empty:
        better = pareto_df[pareto_df["total_time_hrs"] < solution["total_time_hrs"]]
        if not better.empty:
            nxt = better.iloc[0]
            extra_rs = round(nxt["total_cost"] - solution["total_cost"], 1)
            saved_hrs = round(solution["total_time_hrs"] - nxt["total_time_hrs"], 1)
            if extra_rs > 0 and saved_hrs > 0:
                st.caption(f"💡 **Trade-off Insight:** Spending **₹{extra_rs} more** saves you **{saved_hrs} hours/month**.")

# ==========================================
# 8. ROUTE BREAKDOWN & ADJACENCY MATRIX
# ==========================================
with st.expander("🔍 View Step-by-Step Route Segments & Adjacency Matrix"):
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Fastest Route Segments**")
        st.dataframe(pd.DataFrame(fast_route["segments"]), use_container_width=True)
    with c2:
        st.markdown("**Budget Route Segments**")
        st.dataframe(pd.DataFrame(budget_route["segments"]), use_container_width=True)

    st.markdown("**Distance Adjacency Matrix (km — Shortest Direct Edge)**")
    mat = pd.DataFrame(np.inf, index=node_list, columns=node_list)
    np.fill_diagonal(mat.values, 0.0)
    for u, v, d, _ in EDGES:
        mat.loc[u, v] = min(mat.loc[u, v], d)
        mat.loc[v, u] = min(mat.loc[v, u], d)
    st.dataframe(mat.replace(np.inf, "—"), use_container_width=True)
