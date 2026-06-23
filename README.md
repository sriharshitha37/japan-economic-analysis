# 🇯🇵 Japan Economic Analysis Dashboard

**[View the Live Interactive Demo Here🚀](https://japan-economic-analysis.streamlit.app)**

A data-driven, interactive Streamlit web application analyzing Japan's triple demographic crisis—a collapsing birth rate, a rapidly aging population, and a shrinking labor force. 

This dashboard visualizes the severe economic implications of this decline, specifically focusing on the projected IT worker shortage of 790,000 by 2030, and explores how tech talent from the Global South (like India and Vietnam) is uniquely positioned to bridge this critical gap.

---

## ✨ Key Features

*   **Live Data Integration:** Automatically fetches up-to-date macroeconomic and demographic data via the **World Bank API** (`wbgapi`).
*   **Predictive Forecasting:** Utilizes SciPy linear regression models to forecast Japan's population, labor force, and fertility rates up to the year 2030.
*   **Premium SaaS UI:** Features a completely custom-styled sidebar, hidden native Streamlit elements, and a sleek dark-mode glassmorphism design.
*   **Interactive Data Visualizations:** Built with Plotly Express and Graph Objects for dynamic, hoverable area charts, bar graphs, and line series.
*   **Comparative Global Analysis:** Contrasts Japan's demographic trajectory (median age 50.4) with the booming STEM output of Global South nations.

---

## 📊 Dashboard Sections

1.  **📊 Overview:** High-level metrics on GDP vs. Labor Force trends and the critical Birth/Death rate crossover.
2.  **👥 Population Crisis:** A deep dive into fertility rates falling below the replacement level and shifting age structures.
3.  **💹 Economic Impact:** Visualizes the decoupling of GDP from workforce size and projects the widening IT talent deficit.
4.  **🌏 Global Talent Gap:** Highlights the strategic demographic complementarity between Japan and nations like India, Bangladesh, and Sri Lanka.
5.  **🔮 2030 Forecast:** Statistical projections confirming structural, non-random demographic decline over the next decade.

---

## 🛠️ Tech Stack

*   **Frontend / Framework:** [Streamlit](https://streamlit.io/)
*   **Data Manipulation:** [Pandas](https://pandas.pydata.org/), [NumPy](https://numpy.org/)
*   **Data Visualization:** [Plotly](https://plotly.com/python/)
*   **Statistical Modeling:** [SciPy](https://scipy.org/)
*   **Data Sourcing:** [wbgapi](https://pypi.org/project/wbgapi/) (World Bank API)

---

## 🚀 Local Installation & Setup

To run this dashboard locally on your machine, follow these steps:

**1. Clone the repository**
```bash
git clone https://github.com/sriharshitha37/japan-economic-analysis.git
cd japan-economic-analysis
```

**2. Create a virtual environment (Recommended)**
```
python -m venv venv
source venv/bin/activate 
```

**3. Install dependencies**
```
pip install -r requirements.txt
```

**4. Run the application**
```
streamlit run app.py
```
The app will automatically open in your default web browser at ```http://localhost:8501```.

---
📡 Data Sources
---
* This project aggregates and models data from the following verified international organizations:
* World Bank: Historical GDP, population, trade balance, and labor force metrics.
* METI (Japan Ministry of Economy, Trade and Industry): IT worker shortage projections.
* UN & UNESCO: Median age statistics and global STEM graduate output.
