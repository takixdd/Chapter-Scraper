import customtkinter
from import_images import resource_path
from scrap import chapter_scraper
from database import add_new_link_to_database
from db_login import cursor
from db_login import row_count
from title_scrap import title_scrapped
from PIL import Image, ImageTk
from tkinter import ttk
import pandas as pd
from db_login import engine
import webbrowser
import os

customtkinter.set_appearance_mode("dark")
customtkinter.set_default_color_theme("blue")

appWidth, appHeight = 800, 700
iconpath = resource_path(r'logo\animu.ico')
img = customtkinter.CTkImage(light_image=Image.open(r"static\star.png"), size=(20, 20))
img_cover_folder = r'static'

class MainWindow(customtkinter.CTk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Chapter Scraper")
        self.iconbitmap(False, iconpath)
        self.geometry(f"{appWidth}x{appHeight}")
        self.resizable(0, 0)
        self.frame = customtkinter.CTkFrame(self, width=appWidth-1, height=appHeight-1, border_width=1).grid(row=0, column=0, padx=1, pady=1)


        self.new_link_label = customtkinter.CTkLabel(self, text="Add new manga", fg_color=("#dbdbdb", "#2b2b2b"))
        self.new_link_label.grid(row=0, column=0, columnspan=1, padx=145, pady=20, sticky="sw")
        self.add_new_link = customtkinter.CTkEntry(self, width=300, height=40, border_width=1, justify='center')
        self.add_new_link.grid(row=0, column=0, columnspan=1, padx=15, pady=15, sticky="s")
        self.add_button = customtkinter.CTkButton(self, text='ADD NEW', fg_color="#80669d", text_color="white", hover_color="#a881af", width=75, height=35, border_width=1, command=self.add_link)
        self.add_button.grid(row=0, column=0, columnspan=1, padx=170, pady=17, sticky="se")
        self.added_label = customtkinter.CTkLabel(self, text="", fg_color=("#dbdbdb", "#2b2b2b"))
        self.added_label.grid(row=0, column=0, columnspan=1, padx=15, pady=55, sticky="s")

        self.add_button = customtkinter.CTkButton(self, text='EXIT', fg_color="#80669d", text_color="white", hover_color="#B22222", width=45, height=30, border_width=1, command=self.close)
        self.add_button.grid(row=0, column=0, columnspan=1, padx=10, pady=17, sticky="se")

        self.run_scraping_label = customtkinter.CTkLabel(self, text="Run scraping", fg_color=("#dbdbdb", "#2b2b2b"))
        self.run_scraping_label.grid(row=0, column=0, columnspan=1, padx=2, pady=10, sticky="n")
        self.run_scraping_button = customtkinter.CTkButton(self, image=img, text='SCRAP CHAPTERS', fg_color="#80669d", text_color="white", hover_color="#a881af", width=75, height=35, border_width=1, command=self.scrap_chapters)
        self.run_scraping_button.grid(row=0, column=0, columnspan=1, padx=2, pady=40, sticky="n")
        self.count_label = customtkinter.CTkLabel(self, text=f"Mangas in \ndatabase: {row_count}", fg_color=("#dbdbdb", "#2b2b2b"))
        self.count_label.grid(row=0, column=0, columnspan=1, padx=8, pady=15, sticky="sw")

        self.treestyle = ttk.Style()
        self.treestyle.theme_use('classic')
        self.treestyle.configure('Treeview.Heading', background=("#dbdbdb", "#2b2b2b"), foreground="white", font=(None, 12))
        self.treestyle.configure("Treeview", font=(None, 11),
                            background=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            foreground=customtkinter.ThemeManager.theme["CTkLabel"]["text_color"][1],
                            fieldbackground=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            borderwidth=1)
        self.treestyle.map('Treeview', background=[('selected', customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1])], foreground=[('selected', customtkinter.ThemeManager.theme["CTkButton"]["fg_color"][1])])
        self.bind("<<TreeviewSelect>>", lambda event: self.focus_set())

        self.chapter_tree = ttk.Treeview(self, height=25, show='headings', columns=('Title', 'Web_link', 'Latest Chapter', 'Upload Date', 'Days Ago'))
        self.treescroll = customtkinter.CTkScrollbar(self, command=self.chapter_tree.yview, fg_color=("#dbdbdb", "#2b2b2b"))
        self.chapter_tree.configure(yscrollcommand=self.treescroll.set, selectmode="extended")
        self.treescroll.grid(row=0, column=0, sticky="ne", padx=7, pady=90, ipady=160)

        self.treeview()

        self.open_url_button = customtkinter.CTkButton(self, text='Show all mangas', fg_color="#80669d", text_color="white", hover_color="#a881af", width=60, height=30, border_width=1, command=self.treeview)
        self.open_url_button.grid(row=0, column=0, columnspan=1, padx=50, pady=15, sticky="ne")

        self.image1 = resource_path(fr'static/manga.png')
        self.imga = ImageTk.PhotoImage(Image.open(self.image1))
        self.img_label = customtkinter.CTkLabel(self, image=self.imga, text='')
        self.img_label.grid(row=0, column=0, columnspan=1, padx=20, pady=150, sticky="nw")
        self.chapter_tree.bind("<<TreeviewSelect>>", self.on_treeview_select)

        self.chapter_tree.tag_configure("red_tag", foreground="#E2A8F5")
        self.chapter_tree.tag_configure("yellow_tag", foreground="#F5F5CF")

    def add_link(self):
        link = self.add_new_link.get()
        if 'https' in link:
            self.added_label.configure(text=f"{title_scrapped(link)}", text_color="#80669d")
            add_new_link_to_database(link)
        self.add_new_link.delete(0, 'end')

        count_query = "SELECT COUNT(*) FROM link_list"
        cursor.execute(count_query)
        new_count = cursor.fetchone()[0]
        self.count_label.configure(text=f"Mangas in \ndatabase: {new_count}")

    def scrap_chapters(self):
        chapter_scraper()

        mysql_df = "SELECT * FROM detected_list"

        df = pd.read_sql(mysql_df, engine)

        # Clear data in treeview on every refresh
        self.chapter_tree.delete(*self.chapter_tree.get_children())

        self.treestyle.configure("Treeview", font=(None, 13), background=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1], foreground='#A8F6AA', fieldbackground=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1], borderwidth=1)
        self.chapter_tree.column("Title", anchor='w', stretch=False, width=300)
        self.chapter_tree.heading("Title", text="Title")
        self.chapter_tree.column("Web_link", anchor='center', stretch=False, width=1)
        self.chapter_tree.heading("Web_link", text="Web link")
        self.chapter_tree.column("Latest Chapter", anchor='w', stretch=False, width=1)
        self.chapter_tree.heading("Latest Chapter", text="Chapter Name")
        self.chapter_tree.column("Upload Date", anchor='w', stretch=False, width=120)
        self.chapter_tree.heading("Upload Date", text="Uploaded")
        self.chapter_tree.column("Days Ago", anchor='e', stretch=False, width=100)
        self.chapter_tree.heading("Days Ago", text="Days Ago")
        self.chapter_tree.grid(row=0, column=0, padx=20, pady=90, sticky="ne")

        df2 = df.to_numpy().tolist()
        for row in df2:
            self.chapter_tree.insert("", "end", values=row)

        columns = ['Title', 'Web_link', 'Latest Chapter', 'Upload Date', 'Days Ago']

        # Convert to float to sort values from 1 to last etc
        def convert_to_float(value):
            try:
                return float(value)
            except ValueError:
                return value

        def sort_tree(tv, col, reverse):
            data = [(convert_to_float(tv.set(k, col)), k) for k in tv.get_children('')]
            data.sort(reverse=reverse)

            for index, (_, k) in enumerate(data):
                tv.move(k, '', index)

            tv.heading(col, text=col, command=lambda _col=col: sort_tree(tv, _col, not reverse))

        for col in columns:
            self.chapter_tree.heading(col, text=col, command=lambda _col=col: sort_tree(self.chapter_tree, _col, False))

    def close(self):
        self.destroy()

    def treeview(self):
        mysql_df = "SELECT * FROM chapter_list"

        df = pd.read_sql(mysql_df, engine)
        self.treestyle.configure("Treeview", font=(None, 11),
                            background=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            foreground=customtkinter.ThemeManager.theme["CTkLabel"]["text_color"][1],
                            fieldbackground=customtkinter.ThemeManager.theme["CTkFrame"]["fg_color"][1],
                            borderwidth=1)
        # Clear data in treeview on every refresh
        self.chapter_tree.delete(*self.chapter_tree.get_children())

        self.chapter_tree.column("Title", anchor='w', stretch=False, width=240)
        self.chapter_tree.heading("Title", text="Title")
        self.chapter_tree.column("Web_link", anchor='center', stretch=False, width=1)
        self.chapter_tree.heading("Web_link", text="Web link")
        self.chapter_tree.column("Latest Chapter", anchor='w', stretch=False, width=120)
        self.chapter_tree.heading("Latest Chapter", text="Chapter Name")
        self.chapter_tree.column("Upload Date", anchor='w', stretch=False, width=90)
        self.chapter_tree.heading("Upload Date", text="Uploaded")
        self.chapter_tree.column("Days Ago", anchor='e', stretch=False, width=85)
        self.chapter_tree.heading("Days Ago", text="Days Ago")

        df2 = df.to_numpy().tolist()
        for row in df2:
            days_ago_value = float(row[4])
            values = tuple(row)
            item_id = self.chapter_tree.insert("", "end", values=values)

            if 8 < days_ago_value <= 36:
                self.chapter_tree.item(item_id, tags=("yellow_tag",))
            elif days_ago_value > 36:
                self.chapter_tree.item(item_id, tags=("red_tag",))

        self.chapter_tree.grid(row=0, column=0, padx=20, pady=90, sticky="ne")

        columns = ['Title', 'Web_link', 'Latest Chapter', 'Upload Date', 'Days Ago']

        # Convert to float to sort values from 1 to last etc
        def convert_to_float(value):
            try:
                return float(value)
            except ValueError:
                return value

        def sort_tree(tv, col, reverse):
            data = [(convert_to_float(tv.set(k, col)), k) for k in tv.get_children('')]
            data.sort(reverse=reverse)

            for index, (_, k) in enumerate(data):
                tv.move(k, '', index)

            tv.heading(col, text=col, command=lambda _col=col: sort_tree(tv, _col, not reverse))

        for col in columns:
            self.chapter_tree.heading(col, text=col, command=lambda _col=col: sort_tree(self.chapter_tree, _col, False))

        self.open_url_button = customtkinter.CTkButton(self, text='Open selected url', fg_color="#80669d", text_color="white", hover_color="#a881af", width=60, height=30, border_width=1, command=self.open_selected_url)
        self.open_url_button.grid(row=0, column=0, columnspan=1, padx=50, pady=52, sticky="ne")

    def open_selected_url(self):
        columns = ['Title', 'Web_link', 'Latest Chapter', 'Upload Date', 'Days Ago']

        # Get the selected item
        selected_item = self.chapter_tree.selection()

        if selected_item:
            # Get the URL from the selected row and open it in the default web browser
            url_column_index = columns.index('Web_link')
            url = self.chapter_tree.item(selected_item, 'values')[url_column_index]

            if url:
                webbrowser.open(url)

    def on_treeview_select(self, event):
        self.image1 = resource_path(fr'static/manga.png')
        self.imga = ImageTk.PhotoImage(Image.open(self.image1))
        self.img_label.configure(self, image=self.imga)

        columns = ['Title', 'Web_link', 'Latest Chapter', 'Upload Date', 'Days Ago']
        # Get the selected item
        selected_item = self.chapter_tree.selection()

        if selected_item:
            # Get the data from the selected row
            title_column_index = columns.index('Title')
            title = self.chapter_tree.item(selected_item, 'values')[title_column_index]

            cover_name = f'{title}.png'

            if cover_name in os.listdir(r'static'):
                self.image1 = resource_path(fr'static/{cover_name}')
                self.imga = ImageTk.PhotoImage(Image.open(self.image1))
                self.img_label = customtkinter.CTkLabel(self, image=self.imga, text='')
                self.img_label.grid(row=0, column=0, columnspan=1, padx=10, pady=150, sticky="nw")

if __name__ == "__main__":
    app = MainWindow()
    app.mainloop()