import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd
import time
import openpyxl
import requests
from bs4 import BeautifulSoup
import os
import re
import pandas as pd

def get_pdf_links(url,base_url):
    """Fetch all PDF links from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = base_url  # Base URL of the website
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.pdf'):
            if href.startswith('/'):
                href = base_url + href  # Prepend base URL to relative URL
            pdf_links.append(href)
    return pdf_links

def download_pdfs(links, folder):
    """Download PDFs from a list of links to the specified folder."""
    if not os.path.exists(folder):
        os.makedirs(folder)
    for link in links:
        try:
            response = requests.get(link)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to download {link}: {e}")
            continue

        pdf_name = link.split('/')[-1].split('=')[-1]
        pdf_path = os.path.join(folder, pdf_name)
        try:
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {pdf_name} to {folder}")
        except IOError as e:
            print(f"Failed to save {pdf_name}: {e}")

def download(urls,base_folder="download",base_url = 'http://everyspec.com'):
    for url in urls:
        # Extract the last directory name from the URL path for the subfolder
        base_url = base_url
        subfolder_name = url.replace(base_url, '').lstrip('/').split('/')[0]
        subfolder_path = os.path.join(base_folder, subfolder_name)
        # Fetch and download PDF links
        pdf_links = get_pdf_links(url,base_url)
        download_pdfs(pdf_links, subfolder_path)

#------------------------------------------------------------------------------------

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

def fetch_all_links(url, path, visited=None, max_depth=3, current_depth=0):
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
    download(sub_links)

    for link in sub_links:
        if link not in visited:
            time.sleep(1)  # To avoid overloading the server
            fetch_all_links(link, path, visited, max_depth=max_depth, current_depth=current_depth + 1)

    return visited

def get_and_download__all_links(excel_file, output_file):
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
    get_and_download__all_links(excel_file='firstLevel_URL_Test.xlsx', output_file='secondLevel_URL_Test.xlsx')
