from db_login import mydb
from db_login import cursor


def add_new_link_to_database(link):

  cursor.execute("CREATE TABLE IF NOT EXISTS link_list (LIST VARCHAR(50))")

  cursor.execute("INSERT INTO link_list (LIST) VALUES (%s)", (link,))

  for _ in cursor:
    pass

  # Create a temporary table with an auto-incremented column
  cursor.execute("CREATE TEMPORARY TABLE temp_link_list SELECT DISTINCT LIST FROM link_list")

  # Drop the original table
  cursor.execute("DROP TABLE IF EXISTS link_list")

  # Create new link_list without duplicates
  cursor.execute("CREATE TABLE IF NOT EXISTS link_list AS SELECT * FROM temp_link_list")
  cursor.execute("DROP TABLE IF EXISTS temp_link_list")

  for _ in cursor:
    pass

  cursor.execute("SELECT * FROM link_list")
  result = cursor.fetchall()

  mydb.commit()
