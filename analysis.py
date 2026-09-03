"""Sample sales analysis: load, summarize, and chart revenue by region."""

import pandas as pd
import matplotlib.pyplot as plt

DATA_PATH = "data/sales_sample.csv"
OUTPUT_CHART = "output/revenue_by_region.png"


def load_data(path: str) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["date"])
    df["revenue"] = df["units_sold"] * df["unit_price"]
    return df


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    return (
        df.groupby("region")
        .agg(total_units=("units_sold", "sum"), total_revenue=("revenue", "sum"))
        .sort_values("total_revenue", ascending=False)
    )


def plot_revenue_by_region(summary: pd.DataFrame, output_path: str) -> None:
    ax = summary["total_revenue"].plot(kind="bar", color="steelblue")
    ax.set_ylabel("Revenue ($)")
    ax.set_title("Total Revenue by Region")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()


if __name__ == "__main__":
    df = load_data(DATA_PATH)
    summary = summarize(df)
    print(summary)
    plot_revenue_by_region(summary, OUTPUT_CHART)
    print(f"\nChart saved to {OUTPUT_CHART}")
