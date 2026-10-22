from pathlib import Path

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from simulator import (
    compare_policies,
    evaluate_multiple_seeds,
    load_products,
    simulate_policy,
)

st.set_page_config(
    page_title="FreshMargin | Near-Expiry Pricing Intelligence",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded",
)

ROOT = Path(__file__).parent
DATA_PATH = ROOT / "data" / "products.csv"

# Theme and compact CSS for a polished dashboard without external image assets.
st.markdown(
    """
    <style>
      :root { --fm-green:#087f5b; --fm-deep:#102a24; --fm-mint:#d9f7e9; --fm-ink:#182b27; --fm-muted:#667873; }
      .stApp {background:linear-gradient(180deg,#f5faf7 0%,#f7f9fc 42%,#f5f7fb 100%); color:var(--fm-ink);}
      [data-testid="stHeader"] {background:rgba(245,250,247,.88);}
      .block-container {padding-top:2.6rem !important;padding-bottom:2.7rem;max-width:1580px;}
      /* Strip any default Streamlit container surface that can create the pale box. */
      /* Remove Streamlit's default surfaces around the hero and its markdown block. */
      div[data-testid="stVerticalBlockBorderWrapper"],
      div[data-testid="stVerticalBlockBorderWrapper"] > div,
      div[data-testid="stVerticalBlockBorderWrapper"] > div > div,
      div[data-testid="stVerticalBlock"] > div:has(.hero),
      div[data-testid="stMarkdown"]:has(.hero),
      div[data-testid="stMarkdown"]:has(.hero) > div,
      div[data-testid="stElementContainer"]:has(.hero) {
          background: transparent !important;
          background-color: transparent !important;
          border: 0 !important;
          outline: 0 !important;
          box-shadow: none !important;
          padding-left: 0 !important;
          padding-right: 0 !important;
      }
      div[data-testid="stVerticalBlockBorderWrapper"]::before,
      div[data-testid="stVerticalBlockBorderWrapper"]::after,
      div[data-testid="stMarkdown"]:has(.hero)::before,
      div[data-testid="stMarkdown"]:has(.hero)::after {display:none !important; content:none !important;}
      .hero {position:relative;isolation:isolate;overflow:hidden;padding:2.7rem 2.8rem;border-radius:24px;min-height:270px;width:100%;box-sizing:border-box;margin-top:14px;
             background:radial-gradient(circle at 90% 10%,rgba(95,234,173,.28),transparent 28%),
                        linear-gradient(120deg,#102a24 0%,#12563f 55%,#087f5b 100%);
             color:#fff;border:1px solid rgba(255,255,255,.15);margin-bottom:1.2rem;
             box-shadow:0 16px 38px rgba(16,42,36,.14);animation:hero-enter .85s cubic-bezier(.2,.75,.25,1) both;}
      .hero:before {content:"";position:absolute;z-index:-1;width:360px;height:360px;right:-100px;top:-190px;border-radius:50%;background:rgba(104,255,190,.17);filter:blur(5px);animation:glow-drift 8s ease-in-out infinite alternate;}
      .hero:after {content:"";position:absolute;z-index:-1;top:-40%;left:-55%;width:32%;height:180%;transform:rotate(18deg);background:linear-gradient(90deg,transparent,rgba(255,255,255,.09),transparent);animation:hero-shine 8s ease-in-out 1.2s infinite;pointer-events:none;}
      .hero h1 {font-size:3.15rem;line-height:1.12;letter-spacing:-.045em;font-weight:850;margin:0 0 .35rem 0;color:#fff;animation:text-rise .8s .12s both;}
      .hero p {font-size:1.18rem;line-height:1.65;margin:0;color:#d6f4e5;max-width:760px;animation:text-rise .8s .25s both;}
      .hero-top {display:flex;align-items:center;gap:10px;margin-bottom:1rem;color:#a9efd0;font-size:.82rem;font-weight:800;letter-spacing:.14em;text-transform:uppercase;animation:text-rise .7s both;}
      .hero-dot {display:inline-block;width:8px;height:8px;border-radius:50%;background:#67e8a5;box-shadow:0 0 0 5px rgba(103,232,165,.13);animation:dot-pulse 2s ease-in-out infinite;}
      .hero-pill {display:inline-block;margin-top:1.25rem;padding:.5rem .85rem;border:1px solid rgba(215,255,234,.28);border-radius:999px;color:#e2fff0;background:rgba(255,255,255,.08);font-size:.78rem;animation:text-rise .8s .4s both;transition:background .25s,transform .25s;}
      .hero-pill:hover {background:rgba(255,255,255,.16);transform:translateY(-2px);}
      @keyframes hero-enter {from{opacity:0;transform:translateY(14px) scale(.99)}to{opacity:1;transform:translateY(0) scale(1)}}
      @keyframes text-rise {from{opacity:0;transform:translateY(12px)}to{opacity:1;transform:translateY(0)}}
      @keyframes dot-pulse {0%,100%{box-shadow:0 0 0 4px rgba(103,232,165,.12)}50%{box-shadow:0 0 0 8px rgba(103,232,165,.03)}}
      @keyframes glow-drift {from{transform:translate(-10px,0) scale(.95)}to{transform:translate(-45px,30px) scale(1.12)}}
      @keyframes hero-shine {0%,65%{left:-55%;opacity:0}75%{opacity:1}100%{left:130%;opacity:0}}
      div[data-testid="stMetric"] {transition:transform .22s ease,box-shadow .22s ease,border-color .22s ease;}
      div[data-testid="stMetric"]:hover {transform:translateY(-3px);box-shadow:0 10px 24px rgba(18,54,42,.09);border-color:#b9dfcb;}
      div[data-testid="stTabs"] button {transition:background .2s ease,color .2s ease,transform .2s ease;}
      div[data-testid="stTabs"] button:hover {transform:translateY(-1px);}
      @media (prefers-reduced-motion: reduce) {*,*::before,*::after{animation-duration:.01ms !important;animation-iteration-count:1 !important;scroll-behavior:auto !important;transition-duration:.01ms !important;}}
      div[data-testid="stMetric"] {background:rgba(255,255,255,.96);border:1px solid #e0eae5;padding:15px 17px;border-radius:17px;box-shadow:0 5px 18px rgba(18,54,42,.045);min-height:128px;height:100%;box-sizing:border-box;}
      div[data-testid="stMetricDelta"] {white-space:nowrap;}
      div[data-testid="stColumn"] > div[data-testid="stVerticalBlock"] {height:100%;}
      div[data-testid="stMetricLabel"],div[data-testid="stMetricLabel"] p {color:#62736d !important;font-size:.82rem;font-weight:650;}
      div[data-testid="stMetricValue"],div[data-testid="stMetricValue"] div {color:#123d2e !important;font-weight:800;letter-spacing:-.025em;}
      div[data-testid="stMetricDelta"] {font-weight:700;}
      .section-note {color:#667873;font-size:.9rem;}
      .eyebrow {text-transform:uppercase;letter-spacing:.12em;font-size:.72rem;font-weight:800;color:#087f5b;margin-bottom:.3rem;}
      .insight-card {background:#fff;border:1px solid #e0eae5;border-radius:17px;padding:1.15rem 1.2rem;min-height:145px;box-shadow:0 5px 18px rgba(18,54,42,.04);}
      .insight-title {font-size:.75rem;font-weight:800;letter-spacing:.07em;color:#71817b;margin-bottom:.55rem;}
      .insight-value {font-size:1.6rem;font-weight:850;color:#123d2e;line-height:1.25;}
      .insight-copy {font-size:.84rem;color:#667873;margin-top:.55rem;line-height:1.5;}
      .section-banner {background:linear-gradient(90deg,#e5f8ee,#f4fbf7);border:1px solid #cfeadb;border-left:4px solid #0b8a60;padding:.9rem 1rem;border-radius:12px;color:#244b3a;margin:.55rem 0 1rem 0;}
      div[data-testid="stTabs"] {margin-top:.3rem;}
      div[data-testid="stTabs"] button {font-weight:700;border-radius:10px;padding:.65rem .9rem;}
      div[data-testid="stTabs"] button[aria-selected="true"] {background:#e2f6eb;color:#087f5b;}
      div[data-testid="stTabs"] [data-baseweb="tab-highlight"] {background:#087f5b;}
      .small-heading {font-size:1.08rem;font-weight:700;margin-bottom:.25rem;}
      [data-testid="stSidebar"] {background:#edf5f0;border-right:1px solid #dce8e1;}
      [data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 {color:#123d2e;}
      .stButton>button[kind="primaryFormSubmit"],.stButton>button[kind="primary"] {border-radius:11px;font-weight:750;}
      div[data-testid="stPlotlyChart"] {background:#fff;border:1px solid #e6ede9;border-radius:16px;padding:.35rem;}
      div[data-testid="stDataFrame"] {border:1px solid #e2ebe6;border-radius:13px;overflow:hidden;}
      hr {border-color:#e1eae5;}
      @media (max-width: 768px) {.hero{padding:1.45rem;min-height:0;border-radius:18px;margin-top:8px}.hero h1{font-size:2.15rem}.hero p{font-size:1rem}.block-container{padding-top:1.5rem !important}}
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown(
    """
    <div class="hero">
      <h1>Freshness meets profitability.</h1>
      <p>Make smarter markdown decisions, protect margins, and turn near-expiry inventory into timely offers.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

try:
    products = load_products(str(DATA_PATH))
except Exception as exc:
    st.error(f"Could not load product data: {exc}")
    st.stop()

with st.sidebar:
    st.markdown("## Control room")
    st.divider()
    st.markdown("## Simulation controls")
    with st.form("simulation_controls"):
        seed = st.number_input("Random seed", min_value=0, max_value=999999, value=42, step=1)
        simulation_days = st.slider("Simulation duration (days)", 7, 60, 30)
        st.markdown("### Markdown policy")
        threshold_2 = st.slider("First markdown when days left are at most", 2, 7, 2)
        discount_2 = st.slider("First markdown discount (%)", 0, 70, 20, step=5)
        threshold_1 = st.slider("Urgent markdown when days left are at most", 1, threshold_2, 1)
        discount_1 = st.slider("Urgent markdown discount (%)", 0, 90, 40, step=5)
        st.markdown("### Demand assumptions")
        demand_sensitivity = st.slider(
            "Customer response to discounts", 0.0, 2.0, 1.0, step=0.1,
            )
        weekday_lift = st.slider("Weekday demand multiplier", 0.5, 1.8, 1.15, step=0.05)
        weekend_lift = st.slider("Weekend demand multiplier", 0.5, 2.0, 1.25, step=0.05)
        run = st.form_submit_button("Run pricing simulation", type="primary", use_container_width=True)

if threshold_1 > threshold_2:
    st.warning("The urgent markdown threshold must not exceed the first markdown threshold.")

params = dict(
    seed=int(seed),
    simulation_days=int(simulation_days),
    threshold_2_days=int(threshold_2),
    discount_2_days=float(discount_2) / 100,
    threshold_1_day=int(threshold_1),
    discount_1_day=float(discount_1) / 100,
    demand_sensitivity=float(demand_sensitivity),
    weekday_lift=float(weekday_lift),
    weekend_lift=float(weekend_lift),
)

# The simulation runs when the user submits the sidebar form. The first page load
# also runs the default settings so the dashboard is not blank.
if run or "simulation_results" not in st.session_state:
    st.session_state["simulation_results"] = compare_policies(products, **params)
fixed, markdown, comparison = st.session_state["simulation_results"]
fm = comparison.loc[comparison["Policy"] == "Fixed Price"].iloc[0]
mm = comparison.loc[comparison["Policy"] == "Markdown"].iloc[0]

waste_reduction = (
    (fm["Units wasted"] - mm["Units wasted"]) / fm["Units wasted"] * 100
    if fm["Units wasted"] else 0.0
)
revenue_change = (
    (mm["Revenue"] - fm["Revenue"]) / fm["Revenue"] * 100
    if fm["Revenue"] else 0.0
)
profit_change = (
    (mm["Gross profit"] - fm["Gross profit"]) / fm["Gross profit"] * 100
    if fm["Gross profit"] else 0.0
)

if run:
    st.session_state["last_run_seed"] = int(seed)
    st.session_state["last_run_days"] = int(simulation_days)

tab_overview, tab_actions, tab_inventory, tab_policy, tab_robustness, tab_optimizer, tab_sensitivity, tab_deals = st.tabs([
    "Executive Overview", "Smart Actions", "Inventory & Expiry", "Policy Comparison",
    "Multi-Seed Evaluation", "Discount Optimizer", "Sensitivity Analysis", "Today's Deals"
])

with tab_overview:
    st.markdown("### Store performance at a glance")
    k1, k2, k3, k4, k5 = st.columns(5)
    k1.metric("Markdown revenue", f"₹{mm['Revenue']:,.0f}", f"{revenue_change:+.1f}% vs fixed")
    k2.metric("Markdown gross profit", f"₹{mm['Gross profit']:,.0f}", f"{profit_change:+.1f}% vs fixed")
    k3.metric("Units wasted", f"{mm['Units wasted']:,}", f"{waste_reduction:+.1f}% reduction")
    k4.metric("Units sold", f"{mm['Units sold']:,}", f"{int(mm['Units sold'] - fm['Units sold']):+d} vs fixed")
    k5.metric("Gross margin", f"{mm['Gross margin (%)']:.1f}%", f"{mm['Gross margin (%)'] - fm['Gross margin (%)']:+.1f} pts vs fixed")

    st.markdown("#### Decision brief")
    brief_a, brief_b, brief_c = st.columns(3)
    with brief_a:
        st.markdown(f"""
        <div class="insight-card">
          <div class="insight-title">WASTE AVOIDED</div>
          <div class="insight-value">{max(0, int(fm['Units wasted'] - mm['Units wasted'])):,} units</div>
          <div class="insight-copy">Estimated products saved from expiry compared with fixed pricing.</div>
        </div>""", unsafe_allow_html=True)
    with brief_b:
        st.markdown(f"""
        <div class="insight-card">
          <div class="insight-title">REVENUE TRADE-OFF</div>
          <div class="insight-value">{revenue_change:+.1f}%</div>
          <div class="insight-copy">Revenue change under markdown pricing. A negative result means less revenue.</div>
        </div>""", unsafe_allow_html=True)
    with brief_c:
        st.markdown(f"""
        <div class="insight-card">
          <div class="insight-title">PROFIT TRADE-OFF</div>
          <div class="insight-value">{profit_change:+.1f}%</div>
          <div class="insight-copy">Gross-profit change after product costs, before operating expenses.</div>
        </div>""", unsafe_allow_html=True)

    left, right = st.columns([1.15, 1])
    with left:
        st.markdown("#### Revenue and gross profit")
        chart_data = comparison.melt(
            id_vars="Policy", value_vars=["Revenue", "Gross profit"],
            var_name="Metric", value_name="Amount"
        )
        fig = px.bar(
            chart_data, x="Metric", y="Amount", color="Policy", barmode="group",
            color_discrete_map={"Fixed Price": "#8b9b94", "Markdown": "#1e8060"},
            labels={"Amount": "Amount (₹)", "Metric": ""},
        )
        fig.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.markdown("#### Stock outcome")
        stock_data = pd.DataFrame({
            "Outcome": ["Sold", "Wasted", "Remaining"],
            "Fixed Price": [
                int(fm["Units sold"]), int(fm["Units wasted"]),
                max(0, int(products["initial_stock"].sum() - fm["Units sold"] - fm["Units wasted"]))
            ],
            "Markdown": [
                int(mm["Units sold"]), int(mm["Units wasted"]),
                max(0, int(products["initial_stock"].sum() - mm["Units sold"] - mm["Units wasted"]))
            ],
        }).melt(id_vars="Outcome", var_name="Policy", value_name="Units")
        fig2 = px.bar(
            stock_data, x="Outcome", y="Units", color="Policy", barmode="group",
            color_discrete_map={"Fixed Price": "#8b9b94", "Markdown": "#1e8060"},
        )
        fig2.update_layout(height=350, margin=dict(l=10, r=10, t=20, b=10), legend_title_text="")
        st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Daily sales and waste")
    daily = pd.concat([fixed.daily, markdown.daily], ignore_index=True)
    if not daily.empty:
        trend = daily.groupby(["day", "policy"], as_index=False).agg(
            revenue=("revenue", "sum"), units_sold=("units_sold", "sum"),
            units_expired=("units_expired", "sum")
        )
        trend["policy"] = trend["policy"].replace({"Fixed Price": "Fixed Price", "Markdown": "Markdown"})
        metric_choice = st.selectbox("Choose daily trend", ["Revenue", "Units sold", "Units wasted"])
        column = {"Revenue": "revenue", "Units sold": "units_sold", "Units wasted": "units_expired"}[metric_choice]
        fig3 = px.line(
            trend, x="day", y=column, color="policy", markers=True,
            color_discrete_map={"Fixed Price": "#8b9b94", "Markdown": "#1e8060"},
            labels={"day": "Simulation day", column: metric_choice, "policy": "Pricing policy"},
        )
        fig3.update_layout(height=340, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig3, use_container_width=True)

with tab_actions:
    st.markdown("### Smart Actions Centre")
    inventory_actions = products.copy()
    inventory_actions["Days until expiry"] = inventory_actions["shelf_life_days"].astype(int)
    inventory_actions["Current price (₹)"] = inventory_actions["original_price"].astype(float)
    inventory_actions["Suggested discount (%)"] = inventory_actions["shelf_life_days"].apply(
        lambda days: discount_1 * 100 if days <= threshold_1
        else discount_2 * 100 if days <= threshold_2 else 0
    )
    inventory_actions["Suggested price (₹)"] = (
        inventory_actions["original_price"] * (1 - inventory_actions["Suggested discount (%)"] / 100)
    ).round(2)
    inventory_actions["Risk level"] = inventory_actions["Days until expiry"].apply(
        lambda days: "HIGH" if days <= threshold_1
        else "WATCH" if days <= threshold_2 else "LOW"
    )
    inventory_actions["Estimated stock value (₹)"] = (
        inventory_actions["initial_stock"] * inventory_actions["unit_cost"]
    ).round(2)
    high_risk = inventory_actions[inventory_actions["Risk level"] == "HIGH"]
    watch_risk = inventory_actions[inventory_actions["Risk level"] == "WATCH"]
    low_risk = inventory_actions[inventory_actions["Risk level"] == "LOW"]

    r1, r2, r3, r4 = st.columns(4)
    r1.metric("High-risk products", len(high_risk), help="Shelf life meets the urgent markdown threshold.")
    r2.metric("Products to watch", len(watch_risk), help="Shelf life meets the first markdown threshold.")
    r3.metric("Low-risk products", len(low_risk))
    r4.metric("Stock cost at risk", f"₹{inventory_actions.loc[inventory_actions['Risk level'] != 'LOW', 'Estimated stock value (₹)'].sum():,.0f}")

    st.markdown("#### Recommended next actions")
    if not high_risk.empty:
        top = high_risk.sort_values("shelf_life_days").iloc[0]
        st.warning(
            f"**Urgent review:** {top['product_name']} has {int(top['Days until expiry'])} day(s) of shelf life in the catalogue. "
            f"The configured rule suggests ₹{top['Suggested price (₹)']:.2f} "
            f"({top['Suggested discount (%)']:.0f}% off). Check stock rotation and local food-safety procedures."
        )
    elif not watch_risk.empty:
        top = watch_risk.sort_values("shelf_life_days").iloc[0]
        st.info(
            f"**Prepare a markdown:** {top['product_name']} is in the watch band. "
            f"The configured rule suggests ₹{top['Suggested price (₹)']:.2f} "
            f"({top['Suggested discount (%)']:.0f}% off) if the rule is activated."
        )
    else:
        st.success("No products currently meet the configured markdown thresholds in this catalogue.")

    st.markdown("#### Expiry risk radar")
    risk_view = inventory_actions[["product_name", "category", "Days until expiry", "initial_stock",
                                   "Current price (₹)", "Suggested discount (%)", "Suggested price (₹)",
                                   "Risk level", "Estimated stock value (₹)"]].sort_values(
        ["Days until expiry", "initial_stock"], ascending=[True, False]
    )
    st.dataframe(
        risk_view.rename(columns={"product_name": "Product", "category": "Category",
                                  "initial_stock": "Opening stock"}),
        use_container_width=True, hide_index=True,
        column_config={
            "Days until expiry": st.column_config.NumberColumn(format="%d days"),
            "Current price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
            "Suggested price (₹)": st.column_config.NumberColumn(format="₹%.2f"),
            "Estimated stock value (₹)": st.column_config.NumberColumn(format="₹%.2f"),
            "Suggested discount (%)": st.column_config.ProgressColumn(min_value=0, max_value=90, format="%.0f%%"),
        }
    )

with tab_inventory:
    st.markdown("### Inventory and expiry monitoring")
    inventory = products.copy()
    inventory["expiry_day"] = inventory["shelf_life_days"]
    inventory["suggested_discount"] = inventory["shelf_life_days"].apply(
        lambda days: discount_1 * 100 if days <= threshold_1
        else discount_2 * 100 if days <= threshold_2 else 0
    )
    inventory["suggested_price"] = (
        inventory["original_price"] * (1 - inventory["suggested_discount"] / 100)
    ).round(2)
    inventory["potential_stock_value"] = (
        inventory["initial_stock"] * inventory["original_price"]
    ).round(2)
    near_expiry = inventory[inventory["shelf_life_days"] <= max(3, threshold_2)].copy()
    c1, c2, c3 = st.columns(3)
    c1.metric("Products in catalogue", len(inventory))
    c2.metric("Total starting units", f"{int(inventory['initial_stock'].sum()):,}")
    c3.metric("Near-expiry product types", len(near_expiry))
    st.markdown("#### Product catalogue")
    display_cols = [
        "product_id", "product_name", "category", "initial_stock", "shelf_life_days",
        "original_price", "unit_cost", "base_daily_demand", "suggested_discount",
        "suggested_price", "potential_stock_value"
    ]
    st.dataframe(
        inventory[display_cols].rename(columns={
            "product_id": "Product ID", "product_name": "Product",
            "category": "Category", "initial_stock": "Initial stock",
            "shelf_life_days": "Shelf life (days)", "original_price": "Original price (₹)",
            "unit_cost": "Unit cost (₹)", "base_daily_demand": "Base daily demand",
            "suggested_discount": "Suggested discount (%)", "suggested_price": "Suggested price (₹)",
            "potential_stock_value": "Stock value (₹)"
        }),
        use_container_width=True, hide_index=True
    )
    st.markdown("#### Near-expiry action list")
    if near_expiry.empty:
        st.success("No products meet the current near-expiry threshold.")
    else:
        st.dataframe(
            near_expiry[["product_name", "category", "shelf_life_days", "original_price",
                         "suggested_discount", "suggested_price"]].rename(columns={
                "product_name": "Product", "category": "Category",
                "shelf_life_days": "Days until expiry", "original_price": "Original price (₹)",
                "suggested_discount": "Recommended discount (%)", "suggested_price": "Suggested price (₹)"
            }),
            use_container_width=True, hide_index=True
        )

with tab_policy:
    st.markdown("### Pricing policy comparison")
    st.dataframe(comparison, use_container_width=True, hide_index=True)
    a, b = st.columns(2)
    with a:
        st.markdown("#### Product-level outcomes")
        product_compare = fixed.product_summary[[
            "product_id", "product_name", "category", "units_sold", "units_expired",
            "revenue", "gross_profit", "waste_rate_pct"
        ]].merge(
            markdown.product_summary[[
                "product_id", "units_sold", "units_expired", "revenue", "gross_profit", "waste_rate_pct"
            ]],
            on="product_id", suffixes=("_fixed", "_markdown")
        )
        product_compare["waste_units_avoided"] = (
            product_compare["units_expired_fixed"] - product_compare["units_expired_markdown"]
        )
        st.dataframe(product_compare.rename(columns={
            "product_name": "Product", "category": "Category",
            "units_sold_fixed": "Sold (fixed)", "units_sold_markdown": "Sold (markdown)",
            "units_expired_fixed": "Wasted (fixed)", "units_expired_markdown": "Wasted (markdown)",
            "revenue_fixed": "Revenue (fixed ₹)", "revenue_markdown": "Revenue (markdown ₹)",
            "gross_profit_fixed": "Profit (fixed ₹)", "gross_profit_markdown": "Profit (markdown ₹)",
            "waste_rate_pct_fixed": "Waste rate (fixed %)",
            "waste_rate_pct_markdown": "Waste rate (markdown %)",
            "waste_units_avoided": "Waste units avoided",
        }), use_container_width=True, hide_index=True)
    with b:
        st.markdown("#### When markdowns were applied")
        if markdown.deals.empty:
            st.info("No markdowns were applied under the current settings.")
        else:
            st.dataframe(markdown.deals.rename(columns={
                "day": "Simulation day", "product_name": "Product", "category": "Category",
                "days_left": "Days left", "original_price": "Original price (₹)",
                "sale_price": "Markdown price (₹)", "discount_pct": "Discount (%)",
                "units_sold": "Units sold"
            }), use_container_width=True, hide_index=True, height=430)


with tab_robustness:
    st.markdown("### Multi-seed evaluation")
    number_of_seeds = st.slider("Number of random seeds", 10, 50, 10, step=5)
    first_seed = st.number_input("Starting seed", min_value=0, max_value=999999, value=100, step=1, key="multi_seed")
    if st.button("Evaluate across seeds", type="primary"):
        seeds = list(range(int(first_seed), int(first_seed) + number_of_seeds))
        with st.spinner("Running repeated simulations..."):
            eval_df = evaluate_multiple_seeds(
                products, seeds=seeds,
                simulation_days=int(simulation_days),
                threshold_2_days=int(threshold_2),
                discount_2_days=float(discount_2) / 100,
                threshold_1_day=int(threshold_1),
                discount_1_day=float(discount_1) / 100,
                demand_sensitivity=float(demand_sensitivity),
                weekday_lift=float(weekday_lift),
                weekend_lift=float(weekend_lift),
            )
        st.session_state["evaluation_results"] = eval_df
    if "evaluation_results" in st.session_state:
        eval_df = st.session_state["evaluation_results"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Average waste reduction", f"{eval_df['waste_reduction_pct'].mean():.1f}%")
        c2.metric("Average revenue change", f"{eval_df['revenue_change_pct'].mean():+.1f}%")
        c3.metric("Average gross profit change", f"{eval_df['profit_change_pct'].mean():+.1f}%")
        fig4 = px.box(
            eval_df.melt(
                id_vars="seed",
                value_vars=["waste_reduction_pct", "revenue_change_pct", "profit_change_pct"],
                var_name="Measure", value_name="Change (%)"
            ),
            x="Measure", y="Change (%)", points="all",
            labels={"Measure": "Metric"},
        )
        fig4.update_layout(height=360, margin=dict(l=10, r=10, t=15, b=10))
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(eval_df.round(2), use_container_width=True, hide_index=True)

# STRETCH GOAL 1: category-wise discount optimization.
with tab_optimizer:
    st.markdown("### Find the best urgent discount for each category")
    discount_steps = st.multiselect(
        "Urgent discount steps to test (%)",
        [10, 15, 20, 25, 30, 35, 40, 45, 50, 60],
        default=[10, 20, 30, 40, 50], key="optimizer_discount_steps"
    )
    if not discount_steps:
        st.warning("Select at least one discount step.")
    elif st.button("Run category optimizer", type="primary", key="run_optimizer"):
        rows = []
        categories = list(products["category"].dropna().unique())
        progress = st.progress(0)
        total = len(categories) * len(discount_steps)
        count = 0
        for category in categories:
            category_products = products[products["category"] == category].copy()
            for candidate in sorted(set(discount_steps)):
                result = simulate_policy(
                    category_products, policy="Markdown",
                    seed=int(seed), simulation_days=int(simulation_days),
                    threshold_2_days=int(threshold_2), discount_2_days=float(discount_2) / 100,
                    threshold_1_day=int(threshold_1), discount_1_day=float(candidate) / 100,
                    demand_sensitivity=float(demand_sensitivity),
                    weekday_lift=float(weekday_lift), weekend_lift=float(weekend_lift),
                )
                summary = result.product_summary
                rows.append({
                    "Category": category, "Urgent discount tested (%)": candidate,
                    "Gross profit (₹)": round(float(summary["gross_profit"].sum()), 2),
                    "Revenue (₹)": round(float(summary["revenue"].sum()), 2),
                    "Units sold": int(summary["units_sold"].sum()),
                    "Units expired": int(summary["units_expired"].sum()),
                })
                count += 1
                progress.progress(count / total)
        trials = pd.DataFrame(rows).sort_values(
            ["Category", "Gross profit (₹)", "Units expired"], ascending=[True, False, True]
        )
        st.session_state["fm_optimizer_trials"] = trials
        st.session_state["fm_optimizer_best"] = trials.groupby("Category", as_index=False).first()
    if "fm_optimizer_best" in st.session_state:
        best = st.session_state["fm_optimizer_best"]
        trials = st.session_state["fm_optimizer_trials"]
        st.markdown("#### Recommended discount by category")
        st.dataframe(best, use_container_width=True, hide_index=True)
        st.markdown("#### Compare tested discount steps")
        category_choice = st.selectbox("Choose a category", best["Category"].tolist(), key="optimizer_category")
        chart_data = trials[trials["Category"] == category_choice].sort_values("Urgent discount tested (%)")
        st.plotly_chart(px.line(chart_data, x="Urgent discount tested (%)", y="Gross profit (₹)", markers=True,
                                title=f"Simulated gross profit — {category_choice}"), use_container_width=True)

# STRETCH GOAL 2: normal shopper response versus half-strength response.
with tab_sensitivity:
    st.markdown("### What if shoppers respond only half as strongly?")
    normal_sensitivity = st.slider("Normal shopper response strength", 0.0, 2.0, float(demand_sensitivity), 0.1,
                                   key="normal_sensitivity")
    if st.button("Run sensitivity comparison", type="primary", key="run_sensitivity"):
        shared = dict(seed=int(seed), simulation_days=int(simulation_days),
                      threshold_2_days=int(threshold_2), discount_2_days=float(discount_2) / 100,
                      threshold_1_day=int(threshold_1), discount_1_day=float(discount_1) / 100,
                      weekday_lift=float(weekday_lift), weekend_lift=float(weekend_lift))
        normal = simulate_policy(products, policy="Markdown", demand_sensitivity=float(normal_sensitivity), **shared)
        half = simulate_policy(products, policy="Markdown", demand_sensitivity=float(normal_sensitivity) / 2, **shared)
        comparison_rows = []
        for label, result, sensitivity_value in [
            ("Normal response", normal, float(normal_sensitivity)),
            ("Half-strength response", half, float(normal_sensitivity) / 2),
        ]:
            summary = result.product_summary
            comparison_rows.append({
                "Scenario": label, "Demand sensitivity": sensitivity_value,
                "Revenue (₹)": round(float(summary["revenue"].sum()), 2),
                "Gross profit (₹)": round(float(summary["gross_profit"].sum()), 2),
                "Units sold": int(summary["units_sold"].sum()),
                "Units expired": int(summary["units_expired"].sum()),
                "Waste rate (%)": round(float(summary["units_expired"].sum()) / max(1, int(summary["initial_stock"].sum())) * 100, 1),
            })
        st.session_state["fm_sensitivity"] = pd.DataFrame(comparison_rows)
    if "fm_sensitivity" in st.session_state:
        df = st.session_state["fm_sensitivity"]
        normal_row, half_row = df.iloc[0], df.iloc[1]
        a, b, c = st.columns(3)
        a.metric("Revenue change", f"₹{half_row['Revenue (₹)'] - normal_row['Revenue (₹)']:+,.0f}")
        b.metric("Gross profit change", f"₹{half_row['Gross profit (₹)'] - normal_row['Gross profit (₹)']:+,.0f}")
        c.metric("Units expired change", f"{int(half_row['Units expired'] - normal_row['Units expired']):+d}")
        st.dataframe(df, use_container_width=True, hide_index=True)
        plot_df = df.melt(id_vars="Scenario", value_vars=["Revenue (₹)", "Gross profit (₹)"],
                          var_name="Metric", value_name="Amount (₹)")
        st.plotly_chart(px.bar(plot_df, x="Metric", y="Amount (₹)", color="Scenario", barmode="group",
                               title="Normal vs half-strength shopper response"), use_container_width=True)

# STRETCH GOAL 3: shopper-facing deals from the current day-one simulation.
with tab_deals:
    st.markdown("### Today's deals")
    deals_result = simulate_policy(
        products, policy="Markdown", seed=int(seed), simulation_days=int(simulation_days),
        threshold_2_days=int(threshold_2), discount_2_days=float(discount_2) / 100,
        threshold_1_day=int(threshold_1), discount_1_day=float(discount_1) / 100,
        demand_sensitivity=float(demand_sensitivity), weekday_lift=float(weekday_lift), weekend_lift=float(weekend_lift),
    )
    day_one = deals_result.daily[(deals_result.daily["day"] == 1) & (deals_result.daily["discount_pct"] > 0)].copy()
    if day_one.empty:
        st.info("No products qualify for a markdown on simulation day 1. Try adjusting the expiry thresholds.")
    else:
        day_one = day_one.drop_duplicates(subset=["product_id"] if "product_id" in day_one.columns else ["product_name"])
        deal_columns = st.columns(3)
        for i, (_, deal) in enumerate(day_one.iterrows()):
            with deal_columns[i % 3]:
                st.markdown("---")
                st.markdown(f"#### {deal['product_name']}")
                st.caption(str(deal["category"]))
                price = float(deal["price"])
                match = products.loc[products["product_name"] == deal["product_name"], "original_price"]
                original = float(match.iloc[0]) if not match.empty else price
                st.markdown(f"**₹{price:,.2f}** · ~~₹{original:,.2f}~~")
                st.success(f"Save {float(deal['discount_pct']):.0f}%")
                st.caption(f"{int(deal['days_left'])} day(s) remaining in the simulation")