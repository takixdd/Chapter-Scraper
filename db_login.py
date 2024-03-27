import mysql.connector
from sqlalchemy import create_engine
from mysql.connector import Error
from CTkMessagebox import CTkMessagebox
import customtkinter

# Your mysql server 
try:
  user = ""
  password = ""
  host = ""
  database = ""

  mydb = mysql.connector.connect(
    user=user,
    password=password,
    host=host,
    database=database,
    auth_plugin="mysql_native_password",
    autocommit=True)

except Error:
  customtkinter.set_appearance_mode("dark")
  customtkinter.set_default_color_theme("blue")
  app = customtkinter.CTk()
  app.withdraw()
  msg = CTkMessagebox(title="Connection Error", message="Error connecting to MySQL database", icon="warning", option_1="Ok")
  response = msg.get()
  if response == "Ok":
    app.destroy()
  app.mainloop()


cursor = mydb.cursor()
engine = create_engine(f"mysql+mysqlconnector://{user}:{password}@{host}/{database}")

# Count how many rows
count_query = "SELECT COUNT(*) FROM link_list"
cursor.execute(count_query)
row_count = cursor.fetchone()[0]

list_query = "SELECT COUNT(*) FROM chapter_list"
cursor.execute(list_query)
real_count = cursor.fetchone()[0]

