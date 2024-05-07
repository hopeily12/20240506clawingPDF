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
    df = df[~df['URL'].str.contains("page")]

    # 保存到本地excel
    df.to_excel(path, index=False)

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

def get_URL(flag,excel_file,output_file):
    #flag = 1：first Level URL；
    #flag = 2：Second Level URL.
    # Load URLs from an Excel file
    excel_file = excel_file
    df = pd.read_excel(excel_file)
    urls = df.iloc[:, 0].dropna().unique()  # Assuming URLs are in the second column
    links_all = []
    if flag == 1:
        for url in urls:
            links = fetch_links(url)
            links_all.extend(links)
            if links:
                print("Found links in First Level URL:{}.".format(url))
            else:
                print("No links found or failed to fetch links in First Level URL.")
    elif flag == 2:   
        for url in urls:
            #考虑到具体标准下可能会有很多的分页
            for i in range(1,21):
                modified_url = url + "?page=" + str(i)
                print(f"Fetching links from: {modified_url}")
                links = fetch_links(modified_url)
                if links:
                    print("Found links in Second Level URL:{}.".format(modified_url))
                    links_all.extend(links)
                else:
                    print("No links found or failed to fetch links in Second Level URL.")
    # Save the collected links to a text file
    write_modify_xlsx(output_file,links_all)

if __name__ == "__main__":
    get_URL(flag=1,
                excel_file = 'firstLevel_URL.xlsx',
                        output_file = 'secondLevel_URL.xlsx')
    get_URL(flag=2,
            excel_file = 'secondLevel_URL.xlsx',
                    output_file = 'thirdLevel_URL.xlsx')
