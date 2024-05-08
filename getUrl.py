import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import pandas as pd

def write_modify_xlsx(path,list):
    # list转dataframe
    df = pd.DataFrame(list, columns=['URL'])
    #删除重复的行
    df = df.drop_duplicates(keep=False)
    #删除有特定字符的行
    # df = df[~df['URL'].str.contains("page")]

    # 保存到本地excel
    df.to_excel(path, index=False)

def fetch_links(url):
    """Fetches hyperlinks that are subdirectories of the given URL."""
    try:
        # Send HTTP request to the URL
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Error accessing the website: {e}")
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

        # Check if the joined URL is within the same domain and subdirectory level or deeper
        if parsed_url.netloc == domain and parsed_url.path.startswith(path):
            links.add(joined_url)

    return links

def get_URL(flag,excel_file,output_file):
    #flag = 1：first Level URL；
    #flag = 2：Second Level URL.
    # Load URLs from an Excel file
    excel_file = excel_file
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
