from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd


@dataclass
class SimulationResult:
    daily: pd.DataFrame
    product_summary: pd.DataFrame
    deals: pd.DataFrame
    policy_name: str


def load_products(path: str = "data/products.csv") -> pd.DataFrame:
    """Load and validate the synthetic grocery product catalogue."""
    df = pd.read_csv(path)
    required = {
        "product_id", "product_name", "category", "initial_stock",
        "unit_cost", "original_price", "shelf_life_days", "base_daily_demand"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"Product dataset is missing columns: {', '.join(sorted(missing))}")
    if (df["initial_stock"] < 0).any() or (df["unit_cost"] < 0).any():
        raise ValueError("Stock and unit cost must be non-negative.")
    if (df["original_price"] <= 0).any():
        raise ValueError("Original prices must be greater than zero.")
    if (df["shelf_life_days"] < 1).any():
        raise ValueError("Shelf life must be at least one day.")
    return df


def _markdown_discount(days_left: int, threshold_2_days: int, discount_2_days: float,
                       threshold_1_day: int, discount_1_day: float) -> float:
    """Return the markdown fraction based on the days remaining before expiry."""
    if days_left <= threshold_1_day:
        return discount_1_day
    if days_left <= threshold_2_days:
        return discount_2_days
    return 0.0


def simulate_policy(
    products: pd.DataFrame,
    policy: str,
    seed: int = 42,
    simulation_days: int = 30,
    threshold_2_days: int = 2,
    discount_2_days: float = 0.20,
    threshold_1_day: int = 1,
    discount_1_day: float = 0.40,
    demand_sensitivity: float = 1.0,
    weekday_lift: float = 1.15,
    weekend_lift: float = 1.25,
) -> SimulationResult:
    """
    Simulate one store. The same seed creates the same demand shocks for
    each product/day, so policy comparisons use common random conditions.
    Stock is received as an initial batch per product and expires according
    to each product's shelf life. No replenishment is assumed in this version.
    """
    if simulation_days < 1:
        raise ValueError("Simulation days must be at least 1.")
    if threshold_1_day > threshold_2_days:
        raise ValueError("The 1-day threshold must be less than or equal to the 2-day threshold.")
    for value in (discount_2_days, discount_1_day):
        if not 0 <= value <= 0.90:
            raise ValueError("Discounts must be between 0% and 90%.")
    if demand_sensitivity < 0:
        raise ValueError("Demand sensitivity cannot be negative.")

    products = products.copy().reset_index(drop=True)
    rng = np.random.default_rng(seed)
    # Pre-generate shocks once, so each policy gets the same random demand variation.
    shocks = rng.normal(loc=1.0, scale=0.18, size=(simulation_days, len(products)))
    stock = products["initial_stock"].astype(int).to_numpy(copy=True)
    initial_stock = stock.copy()
    expired_total = np.zeros(len(products), dtype=int)
    units_sold_total = np.zeros(len(products), dtype=int)
    revenue_total = np.zeros(len(products), dtype=float)
    cost_sold_total = np.zeros(len(products), dtype=float)
    discount_units_total = np.zeros(len(products), dtype=int)
    records: List[dict] = []
    deal_records: List[dict] = []

    for day in range(1, simulation_days + 1):
        weekday = (day - 1) % 7
        calendar_lift = weekend_lift if weekday in (5, 6) else weekday_lift
        for idx, product in products.iterrows():
            if stock[idx] <= 0:
                continue

            days_left = int(product["shelf_life_days"]) - (day - 1)
            if days_left <= 0:
                expired = int(stock[idx])
                expired_total[idx] += expired
                records.append({
                    "day": day, "product_id": product["product_id"],
                    "product_name": product["product_name"], "category": product["category"],
                    "days_left": 0, "price": 0.0, "discount_pct": 0.0,
                    "demand": 0, "units_sold": 0, "units_expired": expired,
                    "revenue": 0.0, "cost_of_goods_sold": 0.0, "gross_profit": 0.0,
                    "ending_stock": 0, "policy": policy
                })
                stock[idx] = 0
                continue

            discount = 0.0
            if policy == "Markdown":
                discount = _markdown_discount(
                    days_left, threshold_2_days, discount_2_days,
                    threshold_1_day, discount_1_day
                )
            price = float(product["original_price"]) * (1 - discount)
            base_demand = float(product["base_daily_demand"])
            # Lower prices increase demand. Sensitivity is adjustable from 0 to 2.
            price_factor = 1 + (discount * 2.2 * demand_sensitivity)
            expiry_urgency = 1.0 + max(0, 4 - days_left) * 0.06
            expected_demand = base_demand * calendar_lift * price_factor * expiry_urgency
            demand = max(0, int(round(expected_demand * max(0.1, shocks[day - 1, idx]))))
            units_sold = min(int(stock[idx]), demand)
            units_expired = 0
            revenue = units_sold * price
            cogs = units_sold * float(product["unit_cost"])
            gross_profit = revenue - cogs
            stock[idx] -= units_sold
            units_sold_total[idx] += units_sold
            revenue_total[idx] += revenue
            cost_sold_total[idx] += cogs
            if discount > 0:
                discount_units_total[idx] += units_sold

            # Any remaining stock expires at the end of the product's shelf life.
            if days_left == 1 and stock[idx] > 0:
                units_expired = int(stock[idx])
                expired_total[idx] += units_expired
                stock[idx] = 0

            records.append({
                "day": day, "product_id": product["product_id"],
                "product_name": product["product_name"], "category": product["category"],
                "days_left": days_left, "price": round(price, 2),
                "discount_pct": round(discount * 100, 1), "demand": demand,
                "units_sold": units_sold, "units_expired": units_expired,
                "revenue": round(revenue, 2), "cost_of_goods_sold": round(cogs, 2),
                "gross_profit": round(gross_profit, 2), "ending_stock": int(stock[idx]),
                "policy": policy
            })
            if policy == "Markdown" and discount > 0:
                deal_records.append({
                    "day": day, "product_name": product["product_name"],
                    "category": product["category"], "days_left": days_left,
                    "original_price": round(float(product["original_price"]), 2),
                    "sale_price": round(price, 2), "discount_pct": round(discount * 100, 1),
                    "units_sold": units_sold
                })

    daily = pd.DataFrame(records)
    if daily.empty:
        daily = pd.DataFrame(columns=[
            "day", "product_id", "product_name", "category", "days_left", "price",
            "discount_pct", "demand", "units_sold", "units_expired", "revenue",
            "cost_of_goods_sold", "gross_profit", "ending_stock", "policy"
        ])

    summary = products[["product_id", "product_name", "category", "original_price", "unit_cost"]].copy()
    summary["initial_stock"] = initial_stock
    summary["units_sold"] = units_sold_total
    summary["units_expired"] = expired_total
    summary["revenue"] = revenue_total.round(2)
    summary["cost_of_goods_sold"] = cost_sold_total.round(2)
    summary["gross_profit"] = (revenue_total - cost_sold_total).round(2)
    summary["discounted_units_sold"] = discount_units_total
    summary["sell_through_pct"] = np.where(
        initial_stock > 0, (units_sold_total / initial_stock * 100).round(1), 0
    )
    summary["waste_rate_pct"] = np.where(
        initial_stock > 0, (expired_total / initial_stock * 100).round(1), 0
    )
    summary["ending_stock"] = np.maximum(0, initial_stock - units_sold_total - expired_total)
    deals = pd.DataFrame(deal_records)
    return SimulationResult(daily=daily, product_summary=summary, deals=deals, policy_name=policy)


def compare_policies(products: pd.DataFrame, **kwargs) -> Tuple[SimulationResult, SimulationResult, pd.DataFrame]:
    fixed = simulate_policy(products, policy="Fixed Price", **kwargs)
    markdown = simulate_policy(products, policy="Markdown", **kwargs)
    comparison = pd.DataFrame([
        _overall_metrics(fixed),
        _overall_metrics(markdown),
    ])
    return fixed, markdown, comparison


def _overall_metrics(result: SimulationResult) -> dict:
    summary = result.product_summary
    revenue = float(summary["revenue"].sum())
    cogs = float(summary["cost_of_goods_sold"].sum())
    gross_profit = float(summary["gross_profit"].sum())
    units_sold = int(summary["units_sold"].sum())
    expired = int(summary["units_expired"].sum())
    initial = int(summary["initial_stock"].sum())
    margin = gross_profit / revenue * 100 if revenue else 0.0
    return {
        "Policy": result.policy_name,
        "Revenue": round(revenue, 2),
        "Gross profit": round(gross_profit, 2),
        "Gross margin (%)": round(margin, 1),
        "Units sold": units_sold,
        "Units wasted": expired,
        "Waste rate (%)": round(expired / initial * 100, 1) if initial else 0.0,
    }


def evaluate_multiple_seeds(products: pd.DataFrame, seeds: List[int], **kwargs) -> pd.DataFrame:
    rows = []
    for seed in seeds:
        fixed = simulate_policy(products, policy="Fixed Price", seed=seed, **kwargs)
        markdown = simulate_policy(products, policy="Markdown", seed=seed, **kwargs)
        fm = _overall_metrics(fixed)
        mm = _overall_metrics(markdown)
        rows.append({
            "seed": seed,
            "fixed_waste": fm["Units wasted"],
            "markdown_waste": mm["Units wasted"],
            "waste_reduction_pct": (
                (fm["Units wasted"] - mm["Units wasted"]) / fm["Units wasted"] * 100
                if fm["Units wasted"] else 0.0
            ),
            "fixed_revenue": fm["Revenue"],
            "markdown_revenue": mm["Revenue"],
            "revenue_change_pct": (
                (mm["Revenue"] - fm["Revenue"]) / fm["Revenue"] * 100
                if fm["Revenue"] else 0.0
            ),
            "fixed_gross_profit": fm["Gross profit"],
            "markdown_gross_profit": mm["Gross profit"],
            "profit_change_pct": (
                (mm["Gross profit"] - fm["Gross profit"]) / fm["Gross profit"] * 100
                if fm["Gross profit"] else 0.0
            ),
        })
    return pd.DataFrame(rows)
