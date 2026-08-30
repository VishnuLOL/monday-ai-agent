# Skylark Drones: Business Intelligence (BI) Agent

A production-grade, real-time Business Intelligence agent built for the founders of Skylark Drones. This application integrates live data from **Monday.com boards** (Deals and Work Orders), cleans and normalizes messy real-world datasets, calculates pipeline valuations, and surfaces critical operational risks instantly.

## 🚀 Live Demo
* **Streamlit Cloud App:** [Link to your deployed app URL]

---

## ✨ Key Features
1. **Live Monday.com API Integration:** Dynamically queries boards using GraphQL, mapping randomized internal column IDs to clean human-readable headers automatically.
2. **Executive Leadership Memo (`/summary`):** Instantly aggregates total pipeline value and flags active operational blockages (stuck/paused work orders) with zero latency.
3. **Operational Risk Management:** Natural language query support to inspect exact blocked accounts, sectors, and execution statuses.
4. **Resilient Data Cleaning (`DataNormalizer`):** Standardizes date formats, handles missing/null numeric fields safely, and strips currency formatting for reliable analytics.

---

## 🛠️ Project Structure
```text
monday-ai-agent/
│
├── app.py                 # Main Streamlit UI & chat router
├── monday_client.py       # GraphQL API client for Monday.com boards
├── data_cleaner.py        # Data sanitization, currency parsing, & schema normalization
├── agent.py               # BI reasoning and response generation layer
├── requirements.txt       # Project Python dependencies
└── DECISION_LOG.md        # Technical architecture and design choices