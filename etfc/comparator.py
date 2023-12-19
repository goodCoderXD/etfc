import pandas as pd

from typing import Any
from etfc.datapull import datapull


def compare_etfs(etf1: str, etf2: str) -> pd.DataFrame:
    etf1_data = datapull(etf1)
    etf2_data = datapull(etf2)

    etf1_df = pd.DataFrame(data=etf1_data[1:], columns=etf1_data[0])
    etf2_df = pd.DataFrame(data=etf2_data[1:], columns=etf2_data[0])

    merged_df = etf1_df.merge(etf2_df, on="Ticker", suffixes=("", "_y"), how="outer")
    merged_df.fillna(0, inplace=True)
    merged_df["Company"] = [
        row["Company"] or row["Company_y"] for i, row in merged_df.iterrows()
    ]
    del merged_df["Company_y"]

    # Calculate drift
    # merged_df["drift"] = (
    #     merged_df[merged_df.columns[2]] - merged_df[merged_df.columns[4]]
    # )
    # breakpoint()

    return merged_df

    # merged = [tuple(r) for r in merged_df.to_numpy()]
    # return [tuple(merged_df.columns), *merged]


def get_stats(merged_df: pd.DataFrame) -> dict[str, Any]:
    breakpoint()
    etf1_pct = merged_df[merged_df.columns[2]]
    etf2_pct = merged_df[merged_df.columns[4]]

    overlap = merged_df[(etf1_pct != 0) & (etf2_pct != 0)]


if __name__ == "__main__":
    get_stats(compare_etfs("SPY", "VOOG"))
