"""Plot strategy balance traces from the CSV logs.

Reads any *_game_logs.csv files in the `logs/` directory (or files passed via
--files) and plots the balance over time for each strategy on a single chart.

Usage:
    python plot_strategies.py            # scans logs/ for *_game_logs.csv and saves a PNG
    python plot_strategies.py --show     # also shows the plot window
    python plot_strategies.py --out out.png --files logs/martingale_game_logs.csv

The script saves the chart to `logs/strategies_comparison.png` by default.
"""
from __future__ import annotations

import argparse
from pathlib import Path
import sys
from typing import List

import pandas as pd
import matplotlib.pyplot as plt


def find_log_files(logs_dir: Path) -> List[Path]:
    if not logs_dir.exists():
        return []
    return sorted(logs_dir.glob("*_game_logs.csv"))


def read_balance_trace(path: Path) -> pd.DataFrame:
    # Read CSV and parse timestamp
    df = pd.read_csv(path)
    if "timestamp" in df.columns:
        try:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        except Exception:
            df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    # Prefer balance_after, fallback to balance_before
    if "balance_after" in df.columns:
        df["balance"] = pd.to_numeric(df["balance_after"], errors="coerce")
    elif "balance_before" in df.columns:
        df["balance"] = pd.to_numeric(df["balance_before"], errors="coerce")
    else:
        df["balance"] = pd.NA
    # Drop rows without timestamp or balance
    if "timestamp" in df.columns:
        df = df.dropna(subset=["timestamp", "balance"])
        df = df.sort_values("timestamp")
    else:
        df = df.dropna(subset=["balance"])  # still keep numeric index
    return df[["timestamp", "balance"]] if "timestamp" in df.columns else df[["balance"]]


def plot_traces(files: List[Path], out_path: Path, show: bool = False) -> None:
    # Try preferred styles in order and fall back to the first available one.
    preferred_styles = ["seaborn-darkgrid", "seaborn", "ggplot", "default"]
    for style in preferred_styles:
        try:
            plt.style.use(style)
            # Informational print to help debugging when run interactively
            # (do not treat as error when style not available)
            # print(f"Using matplotlib style: {style}")
            break
        except OSError:
            # style not available, try next
            continue
    fig, ax = plt.subplots(figsize=(12, 6))

    plotted = 0
    for path in files:
        try:
            df = read_balance_trace(path)
        except Exception as exc:
            print(f"Skipping {path}: read error: {exc}")
            continue

        label = path.stem.replace("_game_logs", "")

        if "timestamp" in df.columns:
            ax.plot(df["timestamp"], df["balance"], label=label)
        else:
            # plot by index if no timestamp
            ax.plot(df.index, df["balance"], label=label)
        plotted += 1

    if plotted == 0:
        print("No valid traces plotted. Check that CSVs exist and have numeric balance columns.")
        return

    ax.set_title("Strategy balance over time")
    ax.set_xlabel("Time")
    ax.set_ylabel("Balance")
    ax.legend()
    ax.grid(True)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path, dpi=150)
    print(f"Saved combined plot to: {out_path}")

    if show:
        plt.show()


def main(argv: List[str] | None = None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    p = argparse.ArgumentParser(description="Plot strategy CSV logs together")
    p.add_argument("--files", "-f", nargs="*", help="Specific CSV log files to plot")
    p.add_argument("--out", "-o", default="logs/strategies_comparison.png", help="Output image path")
    p.add_argument("--show", action="store_true", help="Show the plot window after saving")
    args = p.parse_args(argv)

    if args.files and len(args.files) > 0:
        files = [Path(fp) for fp in args.files]
    else:
        files = find_log_files(Path("logs"))

    if not files:
        print("No log files found in logs/ and none were supplied via --files")
        return 2

    out_path = Path(args.out)
    plot_traces(files, out_path, show=args.show)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
