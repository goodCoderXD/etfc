from textual.app import App, ComposeResult
from textual.widgets import DataTable, Header, Footer, Static
from textual.containers import Container
from textual.reactive import var

from rich.text import Text
from rich.panel import Panel

import pandas as pd


class TableApp(App):
    DEFAULT_CSS = """
    .horizontal {
        layout: horizontal;
    }
    DataTable {
        width: 80%;
        height: 100%;
    }
    .summary {
        height: 100%;
        width: 1fr;
    }
    """

    TITLE = "ETFC"
    SUB_TITLE = "An ETF Comparison Tool"
    BINDINGS = [
        ("1", "sort_etf1", "Sort By ETF1"),
        ("2", "sort_etf2", "Sort By ETF2"),
        ("a", "sort_alpha", "Sort By Comp"),
        ("o", "show_overlap", "Toggle Overlap Only"),
    ]

    overlap_only = var(False)

    def get_etf_names(self) -> tuple[str, str]:
        return (
            self._dataframe.columns[2].replace("%", "").strip(),
            self._dataframe.columns[4].replace("%", "").strip(),
        )

    def action_show_overlap(self):
        self.overlap_only = not self.overlap_only

    def watch_overlap_only(self, overlap_only: bool):
        self.reset_table()

    def action_sort_etf1(self):
        table = self.query_one(DataTable)
        table.sort(
            self._dataframe.columns[2],
            key=lambda value: -float(value.plain.replace("%", "")) if value else 0,
        )

    def action_sort_etf2(self):
        table = self.query_one(DataTable)
        table.sort(
            self._dataframe.columns[4],
            key=lambda value: -float(value.plain.replace("%", "")) if value else 0,
        )

    def action_sort_alpha(self):
        table = self.query_one(DataTable)
        table.sort(self._dataframe.columns[0])

    def __init__(self, *args, dataframe: pd.DataFrame, **kwargs):
        super().__init__(*args, **kwargs)
        self._dataframe = dataframe

    def compose(self) -> ComposeResult:
        yield Header()
        with Container(classes="horizontal"):
            yield DataTable()
            yield Static(classes="summary")
        yield Footer()

    def get_data(self):
        return [
            tuple(self._dataframe.columns),
            *(tuple(r) for r in self._dataframe.to_numpy()),
        ]

    def on_mount(self) -> None:
        table = self.query_one(DataTable)
        data = self.get_data()

        self.show_summary()
        self.reset_table()

    def show_summary(self):
        static = self.query_one(Static)
        static.border_title = "Summary of ETFs"

        static.update(
            Panel(
                f"Hello, [red]World!\nhello\n{len(self._dataframe)}",
                title="Summary of ETFs",
                subtitle="By npengra@nvidia.com",
            )
        )

    def reset_table(self):
        table = self.query_one(DataTable)
        table.clear(True)

        data = self.get_data()

        for column in data[0]:
            table.add_column(column, key=column)

        for ticker, company, etf1_pct, etf1_val, etf2_pct, etf2_val in data[1:]:
            pretty_row = [ticker, company]
            if etf1_pct < etf2_pct:
                etf1_color = "#DB4437"
                etf2_color = "#0F9D58"
            elif etf1_pct > etf2_pct:
                etf1_color = "#0F9D58"
                etf2_color = "#DB4437"
            else:
                etf1_color = "#ffffff"
                etf2_color = "#ffffff"

            if self.overlap_only:
                if any(
                    ((etf1_pct == 0), (etf1_val == 0), (etf2_pct == 0), (etf2_val == 0))
                ):
                    continue

            table.add_row(
                ticker,
                company,
                Text(f"{etf1_pct*100:.3f}%", style=etf1_color) if etf1_pct else None,
                Text(f"${etf1_val:.0f}", style=etf1_color) if etf1_val else None,
                Text(f"{etf2_pct*100:.3f}%", style=etf2_color) if etf2_pct else None,
                Text(f"${etf2_val:.0f}", style=etf2_color) if etf2_val else None,
            )


if __name__ == "__main__":
    from etfc.comparator import compare_etfs

    app = TableApp(compare_etfs("SPY", "VOOG"))
    app.run()
