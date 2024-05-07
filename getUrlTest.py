import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import time

def write_modify_xlsx(path, links):
    """Writes the URLs to an Excel file after removing duplicates."""
    df = pd.DataFrame(links, columns=['URL'])
    df = df.drop_duplicates(keep=False)
    #删除有特定字符的行
    df = df[~df['URL'].str.contains("page")]
    df.to_excel(path, index=False)

def fetch_links(url):
    """Fetches direct hyperlinks from the provided URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing the website {url}: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = url
    domain = urlparse(base_url).netloc
    path = urlparse(base_url).path.rstrip('/')
    links = set()

    for a in soup.find_all('a', href=True):
        href = a.get('href')
        joined_url = urljoin(base_url, href)
        parsed_url = urlparse(joined_url)

        if parsed_url.netloc == domain and parsed_url.path.startswith(path):
            links.add(joined_url)

    return links

def fetch_all_links(url, visited=None):
    """Recursively fetches all links under the given URL."""
    if visited is None:
        visited = set()

    if url in visited:
        return visited

    visited.add(url)
    print(f"Fetching links under {url}")
    sub_links = fetch_links(url)

    for link in sub_links:
        if link not in visited:
            time.sleep(1)  # To avoid overloading the server
            fetch_all_links(link, visited)

    return visited

def get_all_links(excel_file, output_file):
    """Loads URLs from an Excel file and fetches all links for each URL."""
    df = pd.read_excel(excel_file)
    urls = df.iloc[:, 0].dropna().unique()
    all_links = set()

    for url in urls:
        links = fetch_all_links(url)
        all_links.update(links)
        print(f"Found {len(links)} links under {url}")

    write_modify_xlsx(output_file, list(all_links))

if __name__ == "__main__":
    get_all_links(excel_file='firstLevel_URL.xlsx', output_file='secondLevel_URL.xlsx')
