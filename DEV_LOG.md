# FreshMargin — Development Log

**Project:** Markdown Before Waste — Near-Expiry Pricing Intelligence  
**Team:** FreshMargin  
**Technology:** Python, Streamlit, Pandas, NumPy, Plotly

## 1. Project Objective

FreshMargin aims to reduce grocery food waste by applying markdown discounts to products approaching their expiry dates. The goal is to balance waste reduction, product sales, and profitability through an interactive pricing dashboard.

## 2. Key Design Decisions

### Decision 1: Use a Synthetic Dataset

**Reason:** A controlled dataset allows the pricing policy to be tested under repeatable conditions.

**Approach:** Created product and inventory data to simulate demand, stock movement, expiry, and discounting.

### Decision 2: Use Rule-Based Markdown Pricing

**Reason:** Rule-based pricing is straightforward to explain, test, and demonstrate during a hackathon.

**Approach:** Apply discounts according to the remaining shelf life and configured markdown thresholds.

### Decision 3: Build the Dashboard with Streamlit

**Reason:** Streamlit allows the team to demonstrate Python-based analysis through an interactive web interface without building a separate frontend.

**Approach:** Organised the interface around performance metrics, inventory, policy comparisons, and shopper-facing deals.

### Decision 4: Include Multi-Seed Evaluation

**Reason:** Results from a single random simulation may not represent typical performance.

**Approach:** Use multiple random seeds to examine how performance changes under different simulated demand patterns.

### Decision 5: Add a Smart Basket Builder

**Reason:** Showing discounts alone does not demonstrate how customers could use them.

**Approach:** Added a budget-based basket suggestion feature that helps users explore discounted products and potential savings.

## 3. Experiments and Evaluation

The project is designed to compare a markdown pricing policy against a fixed-price baseline.

The main evaluation metrics are:

- Revenue generated
- Gross profit
- Units sold
- Unsold and expired inventory
- Food waste
- Performance across different random seeds

**Evaluation note:** Record the actual results from your simulation here. Do not claim that markdown pricing improved performance until the results support that conclusion.

| Experiment | Purpose | Result |
|---|---|---|
| Fixed-price baseline | Establish a reference point | To be recorded |
| Markdown pricing | Evaluate expiry-based discounts | To be recorded |
| Multi-seed evaluation | Check result consistency | To be recorded |
| Smart Basket Builder | Explore budget-based deal selection | To be recorded |

## 4. AI Assistance

AI assistance was used during development to help with:

- Simplifying and improving Python code.
- Suggesting dashboard layout and interactive features.
- Developing ideas for product filtering, deal sorting, and basket suggestions.
- Troubleshooting code and improving project documentation.

**Human review:** Suggested code and design changes should be reviewed, tested, and adapted by the team before being accepted into the final project.

## 5. Experiments and Rejected Approaches

The following decisions explain the direction of the project. Update them to reflect the approaches actually tested by the team.

### Complex Machine Learning Before a Working Prototype

**Decision:** Start with an explainable, rule-based markdown policy.

**Reason:** A simpler policy provides a clear baseline for evaluating pricing decisions before introducing forecasting complexity.

### A Static Deals Display

**Decision:** Develop an interactive Today's Deals section.

**Reason:** Search, category filters, and sorting make it easier to explore available discounts.

### A Dashboard Showing Metrics Only

**Decision:** Add a Smart Basket Builder.

**Reason:** This connects pricing analytics with a practical customer-facing use case.

**Rejected approaches note:** These are design alternatives considered for the project, not necessarily completed experiments. Replace or supplement them with approaches the team actually tried and rejected.

## 6. Development Challenges

Record issues encountered during implementation, including:

- Errors in inventory updates or simulation logic.
- Problems with dashboard layout or styling.
- Unexpected pricing or discount calculations.
- Differences in results between simulation runs.

For each issue, document the error, its cause, the fix, and how the fix was tested.

## 7. Current Implementation

The dashboard includes:

- Synthetic grocery inventory simulation.
- Configurable markdown pricing.
- Revenue, profit, and waste metrics.
- Inventory and expiry monitoring.
- Pricing policy comparison.
- Multi-seed evaluation.
- Searchable and sortable Today's Deals.
- Budget-based Smart Basket Builder.

## 8. Future Improvements

Potential extensions include:

- Demand forecasting using historical sales.
- Integration with live point-of-sale systems.
- Real-time inventory updates.
- Customer-specific offers.
- Donation recommendations for products unlikely to sell before expiry.

## 9. Final Reflection

FreshMargin explores how transparent pricing rules and interactive analytics can support better decisions for near-expiry grocery products. Future evaluation should establish whether the proposed policy reduces waste while maintaining acceptable profitability across different simulated demand conditions.