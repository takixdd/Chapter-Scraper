import pandas as pd
from bs4 import BeautifulSoup
import requests
import datetime
import re
from db_login import cursor
from db_login import engine
import os
from urllib.parse import urljoin


def chapter_scraper():
    df = pd.DataFrame()

    # Get the data from mysql database table (links to scrap)
    cursor.execute("SELECT DISTINCT LIST FROM link_list")
    result_tuple = cursor.fetchall()

    manga_title = []
    manga_link = []
    page_name = []
    manga_date = []
    day_dif = []

    for link in result_tuple:
        # Format and change data without brackets and commas that I got from mysql database
        link = " ".join(map(str, link))

        web_chapters = requests.get(link).text
        soup = BeautifulSoup(web_chapters, 'lxml')

        date_dict = {"Jan": "1", "Feb": "2", "Mar": "3", "Apr": "4", "May": "5", "Jun": "6",
                       "Jul": "7", "Aug": "8", "Sep": "9", "Oct": "10", "Nov": "11", "Dec": "12"}

        simple_date_day = ()
        simple_date_month = ()
        simple_date_year = ()

        for title_name in soup.find_all(attrs='story-info-right'):
            title = title_name.find('h1').text
            manga_title.append(title)

            # Link added only when website exist, sometimes they change url so there will be more urls in database than actual list
            # need to add here, if link don't find title then delete link from database, would be great to inform user about this also
            manga_link.append(link)

            folder_path = r'static'

            cover_name = f'{title}.png'

            img_name = os.path.join(folder_path, cover_name)

            if not os.path.exists(img_name):
                # Cover scraper, add title_name as image name
                web_chapters = requests.get(link).text
                soup = BeautifulSoup(web_chapters, 'html.parser')

                span_tag = soup.find('span', class_='info-image')
                img_tag = span_tag.find('img')

                # Get the 'src' attribute from the 'img' tag
                img_url = urljoin(link, img_tag['src'])

                img_name = os.path.join(folder_path, cover_name)

                img_data = requests.get(img_url).content
                with open(img_name, 'wb') as f:
                    f.write(img_data)

        for element in soup.find_all(attrs='row-content-chapter'):
            name = element.find('a').text
            chapter_date = element.find(class_ = 'chapter-time text-nowrap').text
            page_name.append(name)
            manga_date.append(chapter_date)

            # Change date for example Dec to 12, Jan to 1 etc
            for i, j in date_dict.items():
                if i in chapter_date:
                    simple_date_month = j

            simple_date_day = re.findall('[0-9]+,', chapter_date)
            simple_date_year = re.findall(',[0-9]+', chapter_date)

            if 'day' in chapter_date:
                days_ago = chapter_date.replace(r'day ago', "")
                days_ago = days_ago.replace(r' ', "")
                day_dif.append(days_ago)

            elif 'hour' in chapter_date:
                days_ago = chapter_date.replace(r'hour ago', "")
                days_ago = days_ago.replace(r' ', "")
                days_ago = round(int(days_ago)/24, 2)
                day_dif.append(days_ago)

            else:
                simple_date_day = simple_date_day[0].replace(r',', '')
                simple_date_year = simple_date_year[0].replace(r',', '20')

                # When was the last chapter
                today = datetime.date.today()
                chapter_day = datetime.date(int(simple_date_year), int(simple_date_month), int(simple_date_day))
                diff = today - chapter_day
                day_dif.append(diff.days)

    df['Title'] = manga_title
    df['Web_link'] = manga_link
    df['Latest Chapter'] = page_name
    df['Upload Date'] = manga_date
    df['Days Ago'] = day_dif

    today = datetime.date.today()
    df['Current Time'] = today

    old_chapter_list = "SELECT * FROM chapter_list"

    df_old = pd.read_sql(old_chapter_list, engine)
    df_detected = pd.DataFrame(columns=df.columns)

    # Detect new chapters and add to new df
    try:
        for new, old, link, title, new_time, old_time in zip(df['Upload Date'], df_old['Upload Date'], df['Web_link'], df['Title'], df['Current Time'], df_old['Current Time']):
            if new == old:
                pass
            elif 'hour' in old:
                if 'hour' in new:
                    hours = r'[0-9]+'
                    new_re = re.findall(hours, new)
                    old_re = re.findall(hours, old)
                    if int(new_re[0]) >= int(old_re[0]):
                        pass
                    else:
                        df_detected.loc[len(df_detected)] = df[df['Title'] == title].iloc[0]
                        print(f'New chapter detected for {title}. Go to {link}')
                elif 'day' in new:
                    if new_time == old_time:
                        pass
                    else:
                        df_detected.loc[len(df_detected)] = df[df['Title'] == title].iloc[0]
                        print(f'New chapter detected for {title}. Go to {link}')
            elif 'day' in old:
                days = r'[0-9]+'
                new_re = re.findall(days, new)
                old_re = re.findall(days, old)
                if int(new_re[0]) >= int(old_re[0]):
                    pass
                else:
                    if new_time == old_time:
                        pass
                    else:
                        df_detected.loc[len(df_detected)] = df[df['Title'] == title].iloc[0]
                        print(f'New chapter detected for {title}. Go to {link}')
            else:
                df_detected.loc[len(df_detected)] = df[df['Title'] == title].iloc[0]
                print(f'New chapter detected for {title}. Go to {link}')

    except KeyError:
        pass

    df_detected.to_sql(name="detected_list", con=engine, if_exists='replace', index=False)

    df.to_sql(name="chapter_list", con=engine, if_exists='replace', index=False)

