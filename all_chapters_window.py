import pandas as pd
from db_login import engine
from all_chapters_window_path import all_window

def read_all_chapters(selected):
    chapter_list = "SELECT * FROM chapter_list"
    df_chapters = pd.read_sql(chapter_list, engine)

    for link, chapter_name, title in df_chapters[['Web_link', 'Latest Chapter', 'Title']].itertuples(index=False):
        if link == selected:
            folder_path = rf'static/{title}'

            all_window(folder_path)
