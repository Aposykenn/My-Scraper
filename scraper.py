import argparse
import csv
import logging
import random
import time
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from typing import Any, Optional, cast

import requests
from bs4 import BeautifulSoup, Tag
from playwright.sync_api import sync_playwright

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("scraper.log"), logging.StreamHandler()],
)

headers = {"User-Agent": "Mozilla/5.0"}


# Function to get a page using requests (3 retries)
def get_page(
    url: str,
    proxies: Optional[dict] = None,
    retries: int = 3,
    timeout: int = 10,
) -> BeautifulSoup | None:
    for attempt in range(retries):
        try:
            response = requests.get(
                url, headers=headers, timeout=timeout, proxies=proxies
            )
            response.raise_for_status()
            soup = BeautifulSoup(response.text, "html.parser")
            return soup
        except requests.RequestException as e:
            logging.error(f"Attempt {attempt + 1} failed for {url}: {e}")
            time.sleep(2)
    logging.exception(f"Failed to fetch {url} after {retries} attempts.")
    return None


# Function to get a page using Playwright
def get_page_playwright(
    url: str, proxies: Optional[dict], timeout: int = 3000
) -> BeautifulSoup | None:
    try:
        with sync_playwright() as p:

            if proxies and "https" in proxies:
                browser = p.chromium.launch(
                    headless=True, proxy={"server": proxies["https"]}
                )
            elif proxies and "http" in proxies:
                browser = p.chromium.launch(
                    headless=True, proxy={"server": proxies["http"]}
                )
            else:
                browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto(url)
            page.wait_for_timeout(timeout * 1000)
            page.wait_for_selector("")
            html = page.content()
            browser.close()
        soup = BeautifulSoup(html, "html.parser")
        return soup
    except Exception as e:
        logging.error(f"An error occurred: {url} - {e}")
        return None


def parse_item(item: Any, options: dict[str, str]) -> tuple[str, str]:
    item = cast(Tag, item)

    # item1 (required)
    tag1, class1 = options["tag1"], options["class1"]
    el1 = item.find(tag1, class_=class1)
    item1 = el1.text.strip() if el1 else "N/A"

    # item2 (optional)
    if "tag2" in options and "class2" in options:
        el2 = item.find(options["tag2"], class_=options["class2"])
        item2 = el2.text.strip() if el2 else "N/A"
    else:
        item2 = "N/A"

    return item1, item2


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
    parser.add_argument(
        "--method", choices=["requests", "playwright"], default="requests"
    )
    parser.add_argument(
        "--timeout", type=int, default=3, help="Timeout for requests in seconds"
    )
    parser.add_argument(
        "--tag1",
        type=str,
        required=True,
        help="Tag for item",
    )
    parser.add_argument(
        "--class1",
        type=str,
        required=True,
        help="Class for item",
    )
    parser.add_argument(
        "--tag2",
        type=str,
        help="second Tag option",
    )
    parser.add_argument(
        "--class2",
        type=str,
        help="second Class option",
    )
    args = parser.parse_args()

    options = {"tag1": args.tag1, "class1": args.class1}
    if args.tag2 and args.class2:
        options["tag2"] = args.tag2
        options["class2"] = args.class2
    data = []
    proxies = {}
    if args.proxy_http:
        proxies["http"] = args.proxy_http
    if args.proxy_https:
        proxies["https"] = args.proxy_https
    if not proxies:
        proxies = None

    for page in range(1, args.pages + 1):
        url = f"{args.url}{args.page_format.replace('{page}', str(page))}"
        logging.info(f"Scraping URL: {url}")
        soup = (
            get_page_playwright(
                url,
                proxies=proxies,
                timeout=args.timeout,
            )
            if args.method == "playwright"
            else get_page(url, proxies=proxies, timeout=args.timeout)
        )

        if not soup:
            logging.warning(f"Failed to fetch page {page}. Continuing to next page.")
            continue

        items = soup.find_all(args.tag, class_=args.class_)
        logging.info(f"Found {len(items)} items in page {page}")
        logging.exception(f"Exception occurred while parsing items on page {page}")
        if not items:
            logging.warning(f"No items found on page {page}. Continuing to next page.")
            continue

        for item in items:
            item_1, item_2 = parse_item(item, options)
            if args.filter.lower() in item_1.lower():
                logging.info(f"item1: {item_1}, item2: {item_2}")
                data.append([item_1, item_2])
        time.sleep(random.uniform(1, 2))
    if not data:
        logging.warning(
            "No data scraped. The CSV file will only contain the header row."
        )
    output_filename = f"output_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["item1", "item2"])
        writer.writerows(data)


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logging.exception(f"An unexpected error occurred: {e}")
