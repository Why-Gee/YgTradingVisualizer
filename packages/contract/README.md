# ygperf

Source-agnostic trading-performance report contract. One `PerfReport` per run; `write_report`/`read_report`. Deps: polars only. No plotly/dash — any producer (backtest, live bot) can import it.
