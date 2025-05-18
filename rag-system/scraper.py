import requests, os, uuid, argparse, time, json
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

SKIP_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".svg", ".mp4", ".mov", ".webm", ".avi", ".mp3", ".wav"}
SKIP_KEYWORDS = {"login", "signin", "signup", "register"}

def should_skip(url):
    url = url.lower()
    return any(url.endswith(ext) for ext in SKIP_EXTENSIONS) or any(k in url for k in SKIP_KEYWORDS)

def get_links(base_url):
    html = requests.get(base_url).text
    soup = BeautifulSoup(html, "html.parser")
    links = [urljoin(base_url, a.get("href")) for a in soup.find_all("a", href=True)]
    return [
        l for l in links
        if urlparse(l).netloc == urlparse(base_url).netloc and not should_skip(l)
    ]

def scrape(url, folder="scraped_data", page_limit=None):
    os.makedirs(folder, exist_ok=True)
    visited = set()
    saved = 0

    def save_page(u):
        nonlocal saved
        if u in visited or should_skip(u): return
        if page_limit is not None and saved >= page_limit: return
        visited.add(u)
        try:
            html = requests.get(u).text
            soup = BeautifulSoup(html, "html.parser")
            text = soup.get_text(separator="\n")
            file_path = os.path.join(folder, f"{uuid.uuid4().hex}.json")
            with open(file_path, "w") as f:
                json.dump({"url": u, "text": text}, f)
            saved += 1
            print(f"✅ [{saved}{f'/{page_limit}' if page_limit else ''}] Saved: {u}")
        except Exception as e:
            print(f"❌ Failed: {u} - {e}")

    save_page(url)
    for link in get_links(url):
        if page_limit is not None and saved >= page_limit:
            break
        save_page(link)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--page-limit", type=int, default=None, help="Max pages to scrape per root URL (default: no limit)")
    parser.add_argument("--update-every-hrs", type=int, default=None, help="Interval to rescrape in hours (default: run once)")
    args = parser.parse_args()

    urls = [
        "https://www.wikiwand.com/en/The_Matrix",
        "https://www.wikiwand.com/en/Dune_(novel)"
    ]

    def run():
        print(f"\n=== Scraping at {time.ctime()} ===")
        for url in urls:
            scrape(url, page_limit=args.page_limit)
        print("✅ Done scraping.\n")

    if args.update_every_hrs is None:
        run()
    else:
        while True:
            run()
            print(f"⏱ Sleeping for {args.update_every_hrs} hours...\n")
            time.sleep(args.update_every_hrs * 3600)
