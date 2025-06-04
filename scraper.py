import argparse
import csv
import random
import time
from typing import Any, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag

headers = {"User-Agent": "Mozilla/5.0"}


def get_page(url: str, proxies: Optional[dict] = None) -> BeautifulSoup | None:
    try:
        response = requests.get(url, headers=headers, timeout=10, proxies=proxies)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        # // you can write print(soup.prettify()) here for debugging
        return soup
    except requests.RequestException as e:
        print(f"An error occurred: {url} - {e}")
        return None


def parse_item(item: Any, tag: str, class_: str) -> tuple[str, str]:
    item = cast(Tag, item)
    title = item.find("span", class_="title")  # Adjust tag/class for title
    price = item.find(
        "div", class_="discount_final_price"
    )  # Adjust tag/class for price
    item_title = title.text.strip() if title else "N/A"
    item_price = price.text.strip() if price else "N/A"
    return item_title, item_price


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True)
    parser.add_argument("--tag", required=True)
    parser.add_argument("--class_", required=True)
    parser.add_argument("--filter", required=True)
    parser.add_argument("--pages", type=int, default=5)
    parser.add_argument("--page_format", default="?page={page}")
    parser.add_argument("--proxy_http", help="HTTP proxy http://proxy_ip:proxy_port")
    parser.add_argument("--proxy_https", help="HTTPS proxy https://proxy_ip:proxy_port")
    args = parser.parse_args()
    data = []
    proxies = None
    if args.proxy_http and args.proxy_https:
        proxies = {
            "http": args.proxy_http,
            "https": args.proxy_https,
        }
    for page in range(1, args.pages + 1):
        url = f"{args.url}{args.page_format.replace('{page}', str(page))}"  # x
        print(f"Scraping URL: {url}")
        soup = get_page(url, proxies=proxies)
        if not soup:
            continue
        items = soup.find_all(args.tag, class_=args.class_)
        print(f"Found {len(items)} items on page {page}")
        for item in items:
            item_title, item_price = parse_item(item, args.tag, args.class_)
            if args.filter.lower() in item_title.lower():
                print(f"Title: {item_title}, Price: {item_price}")
                data.append([item_title, item_price])
        time.sleep(random.uniform(1, 2))
    if not data:
        print("No data scraped. The CSV file will only contain the header row.")
    with open("output.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Title", "Price"])
        writer.writerows(data)
        writer.writerows(data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
