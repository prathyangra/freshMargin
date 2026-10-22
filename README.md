# FreshMargin — Markdown Before Waste

## Files
- `app.py`: Streamlit dashboard and UI.
- `simulator.py`: seeded inventory, demand, expiry, pricing and comparison simulation.
- `data/products.csv`: synthetic 20-product catalogue.
- `requirements.txt`: Python packages.

## Run on Windows
1. Install Python 3.10 or newer.
2. Open Command Prompt in this folder.
3. Install packages:
   `python -m pip install -r requirements.txt`
4. Start the app:
   `python -m streamlit run app.py`
5. Streamlit opens the dashboard in your browser.

## Model notes
This is a synthetic prototype. Initial stock is one batch per product, with no replenishment. Demand is affected by base demand, weekday/weekend multipliers, a seeded random shock, and the discount-response setting. Fixed and markdown policies share the same random demand shocks for a fairer comparison.

The app includes an Overview dashboard, Inventory & Expiry table, Policy Comparison, Multi-Seed Evaluation, and Methodology tab. No external images are required.
