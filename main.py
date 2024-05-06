import requests
from bs4 import BeautifulSoup
import os
import re

def get_pdf_links(url):
    """Fetch all PDF links from the given URL."""
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error fetching the page: {e}")
        return []

    soup = BeautifulSoup(response.text, 'html.parser')
    base_url = 'http://everyspec.com'  # Base URL of the website
    pdf_links = []
    for a in soup.find_all('a', href=True):
        href = a['href']
        if href.endswith('.pdf'):
            if href.startswith('/'):
                href = base_url + href  # Prepend base URL to relative URL
            pdf_links.append(href)
    return pdf_links

def sanitize_filename(name):
    """Sanitize the filename by removing or replacing invalid characters."""
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_pdfs(links, download_folder="downloads"):
    """Download PDFs from a list of links."""
    if not os.path.exists(download_folder):
        os.makedirs(download_folder)

    for link in links:
        try:
            response = requests.get(link)
            response.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to download {link}: {e}")
            continue

        pdf_name = link.split('/')[-1]
        sanitized_name = sanitize_filename(pdf_name)  # Sanitize the filename
        pdf_path = os.path.join(download_folder, sanitized_name)
        try:
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded {sanitized_name}")
        except IOError as e:
            print(f"Failed to save {sanitized_name}: {e}")

def main():
    urls = ['http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-115_NOTICE-1_16836/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-116_12692/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-117_22115/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-118_16851/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-118_NOTICE-1_16853/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-129_4141/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-129_NOTICE-1_25249/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-130B_NOTICE-1_18229/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-131A_21782/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-131A_NOTICE-1_21783/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-131A_NOTICE-2_21784/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-132A_3117/',
            'http://everyspec.com/MIL-HDBK/MIL-HDBK-0099-0199/MIL-HDBK-132A_NOTICE-1_3116/']
    for url in urls:
        download_folder = "D:\\test"  # Define your own path here
        pdf_links = get_pdf_links(url)
        download_pdfs(pdf_links, download_folder)

if __name__ == "__main__":
    main()
