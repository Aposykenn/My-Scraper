# Scraper Project

## Installation

```bash
git clone https://github.com/Aposykenn/Scraper.git
cd scraper
pip install -r requirements.txt
``` 

## Usage

```bash
python scraper.py \
  --url "https://Example.site/explore" \
  --container-tag div --container-class container_world \
  --title-tag span --title-class title \
  --price-tag div --price-class price \
  --pages 10 \
  --timeout 5 \
  --http-proxy http://127.0.0.1:8080
```
Note: --title-tag and --price-tag parameters are examples; they do not need to be literally title or price. You may substitute any valid HTML tag and class that correspond to the elements you wish to extract

## What does it do

- `scraper.py`: 
  1. Downloads the page with using `requests` or `playwright`.
  2. Uses `BeautifulSoup` to find items based on the container tag/class.
  3. if `parse_item` is provided, extracts secondary info (e.g., price). 
  4. writes results to `results.csv`.
- `parse_item`: 
  - extracts item title with given `tag1/class1`.
  - if given `tag2/class2` it gets second info (price etc.).
- If an error occurs, logs it to `scraper.log`.


