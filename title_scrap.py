from bs4 import BeautifulSoup
import requests
from db_login import cursor


def title_scrapped(link):
    web_chapters = requests.get(link).text
    soup = BeautifulSoup(web_chapters, 'lxml')

    for title_name in soup.find_all(attrs='story-info-right'):
        title = title_name.find('h1').text

    cursor.execute("SELECT * FROM link_list")
    result_tuple = cursor.fetchall()

    count = 0
    for x in result_tuple:
        x = "".join(map(str, x))
        if x == link:
            count += 1
        else:
            continue
    if count > 0:
        return f'{title} already exist in database.'
    else:
        return f'Link to {title} successfully added to the database.'