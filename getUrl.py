import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import time
import openpyxl

def write_append_xlsx(path, links):
    """Append new URLs to an Excel file, ensuring no duplicates."""
    # Load or create a new Excel file
    try:
        df_existing = pd.read_excel(path)
        existing_links = set(df_existing['URL'].dropna().unique())
    except FileNotFoundError:
        existing_links = set()

    # Remove duplicates
    new_links = set(links) - existing_links
    if new_links:
        df_new = pd.DataFrame(new_links, columns=['URL'])
        with pd.ExcelWriter(path, mode='a', engine='openpyxl', if_sheet_exists='overlay') as writer:
            df_new.to_excel(writer, index=False, header=False, startrow=writer.sheets['Sheet1'].max_row)

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

def fetch_all_links(url, path, visited=None, max_depth=25, current_depth=0):
    """Recursively fetches all links under the given URL and appends them to the Excel file."""
    if visited is None:
        visited = set()

    if url in visited or current_depth >= max_depth:
        return visited

    visited.add(url)
    try:
        print(f"Fetching links under {repr(url)}")
    except UnicodeEncodeError:
        print(f"Fetching links under [Unprintable URL]")

    sub_links = fetch_links(url)
    write_append_xlsx(path, sub_links)

    for link in sub_links:
        if link not in visited:
            time.sleep(1)  # To avoid overloading the server
            fetch_all_links(link, path, visited, max_depth=max_depth, current_depth=current_depth + 1)

    return visited

def get_all_links(excel_file, output_file):
    """Loads URLs from an Excel file and fetches all links for each URL."""
    df = pd.read_excel(excel_file)
    urls = df.iloc[:, 0].dropna().unique()

    # Create or clear the output Excel file
    with pd.ExcelWriter(output_file) as writer:
        df_empty = pd.DataFrame(columns=['URL'])
        df_empty.to_excel(writer, index=False)

    for url in urls:
        links = fetch_all_links(url, output_file)
        print(f"Found {len(links)} links under {url}")

if __name__ == "__main__":
    get_all_links(excel_file='firstLevel_URL_Test.xlsx', output_file='secondLevel_URL_Test.xlsx')
