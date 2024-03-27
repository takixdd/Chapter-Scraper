import pandas as pd
from bs4 import BeautifulSoup
from db_login import engine
import os
import re
import requests
from urllib.parse import urljoin


def scrap_all(selected):
    chapter_list = "SELECT * FROM chapter_list"
    df_chapters = pd.read_sql(chapter_list, engine)

    for link, title in df_chapters[['Web_link', 'Title']].itertuples(index=False):
        if link == selected:
            # Get HTML from link
            response = requests.get(link)
            html_content = response.text
            soup_all = BeautifulSoup(html_content, 'lxml')

            chapter_elements = soup_all.find_all(class_='chapter-name text-nowrap')
            href_data = [element.get('href') for element in chapter_elements]

            # Get all chapters one by one
            for href in href_data:
                chapter_number = href
                folder_name = re.findall(r'chapter-[0-9]+', chapter_number)

                folder_path = rf'static/{title}/{"".join(folder_name)}'
                if not os.path.exists(folder_path):
                    os.makedirs(folder_path)
                    url = href

                    response = requests.get(url)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.content, 'html.parser')

                        img_tags = soup.find_all('img', src=lambda src: src.endswith('.jpg'))

                        for i, img_tag in enumerate(img_tags):
                            img_url = urljoin(url, img_tag['src'])

                            img_name = os.path.basename(img_url)

                            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 'Referer': url}
                            img_response = requests.get(img_url, headers=headers)

                            if img_response.status_code == 200:
                                img_file_path = os.path.join(folder_path, f"{i + 1}.jpg")
                                with open(img_file_path, 'wb') as f:
                                    f.write(img_response.content)
                                print(f"Image '{img_name}' saved successfully as '{img_file_path}'.")

                            else:
                                print(f"Failed to download image '{img_name}'. Status code:", img_response.status_code)

                    else:
                        print("Failed to fetch web page. Status code:", response.status_code)

                else:
                    print('Already scraped')
                