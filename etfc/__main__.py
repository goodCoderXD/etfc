import click
from etfc.interface import TableApp
from etfc.comparator import compare_etfs


@click.command()
@click.argument("etf1")
@click.argument("etf2")
def etfc(etf1: str, etf2: str):
    """Echoes two stock tickers."""
    dataframe = compare_etfs(etf1.upper(), etf2.upper())
    app = TableApp(dataframe=dataframe)
    app.run()


if __name__ == "__main__":
    etfc()
