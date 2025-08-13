import argparse
import os
import pandas as pd
from notion_client import Client
from dotenv import load_dotenv

# 仅示例核心字段映射，更多字段可按需扩展到 Notion 数据库属性
BASIC_FIELDS = [
    "Ticker","Date","Close","EMA20","MACD","MACD_Signal","ADX","CMF","RSI14","Signal_BUY"
]

def to_notion_number(v):
    try:
        return None if pd.isna(v) else float(v)
    except:
        return None


def main():
    load_dotenv()
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="CSV 文件路径，如 notion_template/daily_metrics.csv")
    args = parser.parse_args()

    api_key = os.getenv("NOTION_API_KEY")
    db_id = os.getenv("NOTION_DATABASE_ID")
    if not api_key or not db_id:
        raise SystemExit("缺少 NOTION_API_KEY / NOTION_DATABASE_ID 环境变量")

    client = Client(auth=api_key)
    df = pd.read_csv(args.csv)

    for _, row in df.iterrows():
        ticker = str(row.get("Ticker"))
        date_str = str(row.get("Date"))

        properties = {
            "Ticker": {"title": [{"text": {"content": ticker}}]},
            "Date": {"date": {"start": date_str}},
            "Close": {"number": to_notion_number(row.get("Close"))},
            "EMA20": {"number": to_notion_number(row.get("EMA20"))},
            "MACD": {"number": to_notion_number(row.get("MACD"))},
            "MACD_Signal": {"number": to_notion_number(row.get("MACD_Signal"))},
            "ADX": {"number": to_notion_number(row.get("ADX"))},
            "CMF": {"number": to_notion_number(row.get("CMF"))},
            "RSI14": {"number": to_notion_number(row.get("RSI14"))},
            "Signal_BUY": {"checkbox": bool(row.get("Signal_BUY")) if pd.notna(row.get("Signal_BUY")) else False},
        }

        # TODO: 若需"更新/去重"，可创建一个唯一键属性（如 Ticker_Date），先查询再更新
        client.pages.create(parent={"database_id": db_id}, properties=properties)

    print(f"Pushed {len(df)} rows to Notion database {db_id}.")


if __name__ == "__main__":
    main()