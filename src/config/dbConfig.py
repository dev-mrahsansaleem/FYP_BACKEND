# Server = 'DESKTOP-U95U5K8'
# Database = 'test'
# Driver = 'SQL Server Native CLient 11.0'
# username = ''
# password = ''
# con = f'mssql://{username}:{password}@{Server}/{Database}?driver={Driver}'
# con_str = f'mssql://@{Server}/{Database}?driver={Driver}'
# engine = create_engine(con_str)
# con = engine.connect()
# data = pd.read_sql_query("SELECT * FROM Images", con)
# print(data.head())

import pyodbc

conn = pyodbc.connect('Driver={SQL Server};'
                      'Server=DESKTOP-U95U5K8;'
                      'Database=FYP_TEMP_DB;'
                      'Trusted_Connection=yes;')
cursor = conn.cursor()
# SQLCommand = (
#     "INSERT INTO checkpython.dbo.new_creat(UserId,TextId) VALUES (?,?)")
# Values = ["admin", 'admin']
# #Processing Query
# cursor.execute(SQLCommand, Values)
# #Commiting any pending transaction to the database.
# conn.commit()
# #closing connection
# print("Data Successfully Inserted")
# conn.close()
