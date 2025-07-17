import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

BASE_URL = "http://localhost:5000"
visited = set()
errors = []

def crawl(url):
    if url in visited:
        return
    visited.add(url)

    try:
        response = requests.get(url, timeout=5)
        print(f"[{response.status_code}] {url}")
        if response.status_code != 200:
            errors.append((url, response.status_code))

        if "text/html" in response.headers.get("Content-Type", ""):
            soup = BeautifulSoup(response.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                next_url = urljoin(url, href)
                # Only stay within localhost
                if urlparse(next_url).netloc == urlparse(BASE_URL).netloc:
                    crawl(next_url)

    except requests.RequestException as e:
        print(f"[ERROR] {url} => {e}")
        errors.append((url, str(e)))

if __name__ == "__main__":
    print(f"Starting crawl on {BASE_URL}")
    crawl(BASE_URL)

    print("\n=== Summary ===")
    print(f"Pages visited: {len(visited)}")
    if errors:
        print(f"Errors found: {len(errors)}")
        for url, err in errors:
            print(f" - {url} => {err}")
    else:
        print("No errors found ✅")
