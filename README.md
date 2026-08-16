# Mortgage vs CAP Simulator

A Streamlit-based application for analyzing the financial benefits of early mortgage prepayment versus investing extra capital in a Capital Accumulation Plan (CAP).

## Overview

This simulator helps you understand the trade-offs between:
- **Early Mortgage Prepayment**: Using extra capital to reduce your remaining mortgage balance
- **CAP Investment**: Investing that extra capital in a Capital Accumulation Plan with expected returns

## Features

- 📊 **Interactive Dashboard**: Visualize mortgage amortization and investment growth
- 📈 **Comparative Analysis**: Side-by-side comparison of both scenarios
- 💾 **Excel Export**: Download amortization schedules and CAP projections
- ⚙️ **Customizable Parameters**:
  - Current mortgage details (remaining capital, interest rate, years)
  - Investment strategy (extra capital timing, CAP returns)
  - Automatic payment savings reinvestment option

## Getting Started

### Prerequisites

- Python 3.14+
- Docker (optional)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the Streamlit app:
   ```bash
   streamlit run app/main.py
   ```

### Docker Usage

Build and run using Docker Compose:

```bash
docker-compose up --build
```

The app will be available at `http://localhost:8501`

## How to Use

1. **Configure Mortgage Details**: Set your current mortgage parameters in the sidebar
2. **Define Investment Schedule**: Enter when and how much extra capital you want to invest
3. **Set CAP Expectations**: Specify the expected annual return on your CAP
4. **Review Results**: Analyze the charts and tables to compare scenarios
5. **Export Data**: Download Excel files for further analysis

## Technical Stack

- **Streamlit**: Interactive web framework
- **Pandas**: Data manipulation and analysis
- **NumPy Financial**: Mortgage calculations
- **Plotly**: Interactive visualizations

## License

See LICENSE file for details