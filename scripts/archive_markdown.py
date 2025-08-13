import os
import datetime as dt
import pandas as pd


def main():
    csv_path = "notion_template/daily_metrics.csv"
    if not os.path.exists(csv_path):
        raise SystemExit(f"缺少 {csv_path}，请先运行 scripts/update_data.py")

    df = pd.read_csv(csv_path, parse_dates=["Date"])
    latest_date = df["Date"].max()
    latest = df[df["Date"] == latest_date].copy()

    buys = latest[latest["Signal_BUY"] == True]
    radars = latest[latest["Signal_Radar"] == True]

    out_dir = "data"
    os.makedirs(out_dir, exist_ok=True)
    out_file = os.path.join(out_dir, f"{str(latest_date)[:10]}-report.md")

    lines = []
    lines.append(f"# Daily Report - {str(latest_date)[:10]}")
    lines.append("")
    lines.append("## BUY Signals")
    if buys.empty:
        lines.append("- None")
    else:
        for _, r in buys.sort_values(["Ticker"]).iterrows():
            lines.append(f"- {r['Ticker']}: Close={r['Close']:.2f}, EMA20={r.get('EMA20', float('nan')):.2f}, ADX={r.get('ADX', float('nan')):.2f}, RSI14={r.get('RSI14', float('nan')):.2f}")

    lines.append("")
    lines.append("## Radar Signals")
    if radars.empty:
        lines.append("- None")
    else:
        for _, r in radars.sort_values(["Ticker"]).iterrows():
            lines.append(f"- {r['Ticker']}: MACD>Signal={bool(r['MACD']>r['MACD_Signal'])}, CMF={r.get('CMF', float('nan')):.3f}, RS={r.get('Relative_Strength', float('nan')):.3f}")

    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"Wrote {out_file}")


if __name__ == "__main__":
    main()