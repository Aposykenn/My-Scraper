# My-Scraper

A basic but growing web scraping tool.  
I'm learning Python through this project and I plan to use it for freelance gigs and personal automation.

---

## Features

- CLI usage with `argparse`
- Scrapes multiple paginated URLs (customizable pattern: `?page={page}`)
- Filters items by keyword
- HTML tag and class-based selection
- HTTP and HTTPS proxy support
- Saves output as CSV
- Error handling + retry safety
- Adjustable delay between requests (anti-ban friendly)

---

## TODO

- Custom output formats (CSV, JSON, TXT)
- Multithreading or asynchronous scraping (maybe)
- Advanced filtering options
- Support for Selenium / Playwright
- CSS selector + XPath / Regex support (maybe)
- `.env` file support
- Basic GUI  
- Streamlit or Flask integration

---

## 🧪 Example Usage

```bash
python scraper.py \
  --url "https://example.com/items" \
  --tag "div" \
  --class_ "item-class" \
  --filter "keyboard" \
  --pages 5 \
  --page_format "?page={page}" \
  --proxy_http "http://127.0.0.1:8080" \
  --proxy_https "https://127.0.0.1:8080"
