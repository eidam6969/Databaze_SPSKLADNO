from pripojeni import *
import mysql.connector

mydb = mysql.connector.connect(
    host = "ip databáze - řekne vám učitel"
    ,user = "řekne vám učitel"
    ,password = "řekne vám učitel"
    ,database = "řekne vám učitel"
)
mycursor = mydb.cursor()

# TODO: zde přijde váš kód ->
mycursor.execute("""CREATE TABLE Uživatel (
id int PRIMARY KEY AUTO_INCREMENT,
jméno char(10) NOT NULL,
příjmení char(20) NOT NULL,
email char(50) NOT NULL UNIQUE
)""")

# tuto část neměnit!
mycursor.execute("""DESCRIBE Uživatel""")
table = str(mycursor.fetchall())
expected = "[('id', 'int(11)', 'NO', 'PRI', None, 'auto_increment'), ('jméno', 'char(10)', 'NO', '', None, ''), ('příjmení', 'char(20)', 'NO', '', None, ''), ('email', 'char(50)', 'NO', 'UNI', None, '')]"
if table == expected:
    print("Tabulka vytvořena správně.")
else:
  print("Tabulka není dle zadání.\nVaše tabulka:")
  print(table)
  print("Očekávaná tabulka:")
  print(expected)
  print("Výpis se liší na pozicích:", [ i for i in range(min(len(table),len(expected))) if table[i] != expected[i] ])

mycursor.execute("""DROP TABLE Uživatel""")
mydb.commit()

mycursor.close()
mydb.close()