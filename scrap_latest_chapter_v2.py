import pandas as pd
from bs4 import BeautifulSoup
from db_login import engine
import os
import re
import requests
from urllib.parse import urljoin
from latest_chapter_window import latest_window


def scrap_latest(selected):
    chapter_list = "SELECT * FROM chapter_list"
    df_chapters = pd.read_sql(chapter_list, engine)

    for link, chapter_name, title in df_chapters[['Web_link', 'Latest Chapter', 'Title']].itertuples(index=False):
        if link == selected:
            latest_chapter_str = re.findall(r'Chapter [0-9]+', chapter_name)
            latest_chapter_str = [chapter.replace('C', '/c') for chapter in latest_chapter_str]
            latest_chapter_str = [chapter.replace(' ', '-') for chapter in latest_chapter_str]
            latest_chapter_link = f'{link}{"-".join(latest_chapter_str)}'
            print(f'{latest_chapter_link}')

            folder_path = rf'static/{title}/{"".join(latest_chapter_str)}'
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

                url = latest_chapter_link
                response = requests.get(url)

                # Checking if there is response from website 200 means it is good
                if response.status_code == 200:
                    # Parse the HTML content using BeautifulSoup
                    soup = BeautifulSoup(response.content, 'html.parser')

                    # Find all img tags with src attribute pointing to JPEG images
                    img_tags = soup.find_all('img', src=lambda src: src.endswith('.jpg'))

                    # Extract the URLs of JPEG images
                    for i, img_tag in enumerate(img_tags):
                        img_url = urljoin(url, img_tag['src'])

                        # Get the file name from the URL
                        img_name = os.path.basename(img_url)

                        # Make a request to download the image emulate Mozilla, there is anty bot system and this will work
                        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3', 'Referer': url}
                        img_response = requests.get(img_url, headers=headers)

                        # Check if the image request was successful (status code 200)
                        if img_response.status_code == 200:
                            # Write the image content to a local file inside the folder
                            img_file_path = os.path.join(folder_path, f"{i + 1}.jpg")
                            with open(img_file_path, 'wb') as f:
                                f.write(img_response.content)
                            print(f"Image '{img_name}' saved successfully as '{img_file_path}'.")

                        else:
                            print(f"Failed to download image '{img_name}'. Status code:", img_response.status_code)

                        # If needed add a delay between requests to avoid rate limiting
                        # time.sleep(0.1)  # Delay of 1 second between requests
                else:
                    print("Failed to fetch web page. Status code:", response.status_code)

            else:
                print('Already scraped')

            latest_window(folder_path)
