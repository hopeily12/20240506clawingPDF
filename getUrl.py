import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def fetch_links(url):
    """Fetches hyperlinks that are subdirectories of the given URL."""
    try:
        # Send HTTP request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
    except requests.RequestException as e:
        print(f"Error accessing the website: {e}")
        return []

    # Parse the HTML content of the page
    soup = BeautifulSoup(response.text, 'html.parser')

    base_url = url
    domain = urlparse(base_url).netloc
    path = urlparse(base_url).path.rstrip('/')
    links = []
    
    # Find all 'a' tags and extract the 'href' attribute, ensuring they are subdirectories of the base URL
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        joined_url = urljoin(base_url, href)  # Resolve relative URLs
        parsed_url = urlparse(joined_url)

        # Check if the joined URL is within the same domain and subdirectory level or deeper
        if parsed_url.netloc == domain and parsed_url.path.startswith(path):
            links.append(joined_url)

    return links

def get_URL(flag):
    #flag = 1：不在终端打印获取的url，而是保存为txt文件；
    #flag = 2：在终端打印获取的url，不保存为txt文件。
    links_all = []
    # Load URLs from an Excel file
    excel_file = 'E:\\20240506clawingPDF\\url.xlsx'  # Replace with the path to your Excel file
    sheet_name = 'total'  # Sheet name or index
    df = pd.read_excel(excel_file, sheet_name=sheet_name)
    urls = df.iloc[:, 1].dropna().unique()  # Assuming URLs are in the first column
    for url in urls:
        for i in range(1,21):
            modified_url = url + "?page=" + str(i)
            print(f"Fetching links from: {modified_url}")
            links = fetch_links(modified_url)
            if links:
                print("Found links:")
                links_all.extend(links)
                if flag == 2:
                    for link in links:
                        print(link)
            else:
                print("No links found or failed to fetch links.")
    if flag == 1:
    # Save the collected links to a text file
        output_file = 'E:\\20240506clawingPDF\\collected_links.txt'  # Specify the path to save the text file
        with open(output_file, 'w') as file:
            for link in links_all:
                file.write(f"{link}\n")  # Write each link on a new line

if __name__ == "__main__":
    get_URL(flag=1)
