# Python Data Analysis Starter

A minimal example project for doing data analysis in Python with pandas.

## Setup

```bash
pip install -r requirements.txt
```

## Run

```bash
python analysis.py
```

This loads `data/sales_sample.csv`, computes total units and revenue per
region, prints the summary, and saves a bar chart to
`output/revenue_by_region.png`.

## Structure

- `data/` — input datasets (CSV)
- `output/` — generated charts and results
- `analysis.py` — the analysis script
