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

if __name__ == "__main__":
    download(urls)
