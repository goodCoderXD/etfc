from decimal import Decimal
from typing import Any

import requests
from bs4 import BeautifulSoup

from etfc.cache import disk_cache

TARGET_URL = "https://www.etfchannel.com/lists/?a=stockholdings&issuer=&symbol={ticker}&sortby=&reverse=&rpp=20&start={start}"
COOKIES = {"slogin": "1700761901", "slogin": "1700761901", "coregval": "ims"}


def parse_percentage(pct: str) -> float:
    return float(Decimal(pct.replace("%", "")) / 100)


def parse_dollar(usd: str) -> float:
    return float(usd.replace("$", "").replace(",", ""))


def get_table_of_stocks(
    ticker: str, start: int, session: requests.Session | None = None
) -> list[tuple[str, str, float, float]]:
    if session:
        payload = session.get(
            TARGET_URL.format(ticker=ticker, start=start),
            cookies=COOKIES,
        )
    else:
        payload = requests.get(
            TARGET_URL.format(ticker=ticker, start=start),
            cookies=COOKIES,
        )
    print(f"Executed {TARGET_URL.format(ticker=ticker, start=start)}")

    raw_text = payload.text
    soup = BeautifulSoup(raw_text, features="html.parser")

    # That's just what the page hardcoded it as
    # And they don't use classes or ids either
    tables = soup.find_all("table", width=420)

    assert tables, start

    matching_tables = [
        table.find("table")
        for table in tables
        if "Stock Holdings Page" in table.text
        and ticker in table.text
        and table.find("table")
    ]

    assert len(matching_tables) == 1, start
    raw_html_data = matching_tables[0]

    # Get a list[list[<td>]]
    raw_html_rows = [
        row.find_all("td")
        for row in raw_html_data.find_all("tr")
        if row.find("td") and len(row.find_all("td")) == 3
    ]
    # Convert the <td> -> str so we have list[tuple[str]]
    raw_rows = [tuple(cell.text for cell in row) for row in raw_html_rows]
    tickers = [
        href.attrs["href"].split("/")[-1]
        if (href := row[0].find("a", href=True))
        else raw_rows[i][0]
        for i, row in enumerate(raw_html_rows)
    ]

    assert len(raw_rows) == len(tickers), start

    cleaned_rows = [
        (
            company.strip().lower(),
            ticker.strip().upper(),
            parse_percentage(pct),
            parse_dollar(usd),
        )
        for (ticker, (company, pct, usd)) in zip(tickers, raw_rows)
    ]

    return cleaned_rows


@disk_cache()
def datapull(ticker: str) -> list[tuple[Any]]:
    table_so_far = []
    tickers_so_far = set()
    session = requests.Session()
    last_start = -1
    for s in range(100):  # while True
        start = len(table_so_far) // 20
        if last_start == start:
            break

        batch_of_stocks = get_table_of_stocks(ticker, start, session=session)
        table_so_far.extend(batch_of_stocks)
        batch_of_tickers = set(map(lambda t: t[1], batch_of_stocks))

        # Check for dupes
        assert (
            not batch_of_tickers & tickers_so_far
        ), f"{start}: {batch_of_tickers & tickers_so_far}"
        tickers_so_far |= batch_of_tickers
        print(f"Pulled: {batch_of_tickers}")
        last_start = start

    return [
        ("Company", "Ticker", f"{ticker} %", f"{ticker} Value (USD)"),
        *table_so_far,
    ]


if __name__ == "__main__":
    df = datapull("SPY")
    print(df)
