import pyodbc
import sqlalchemy
import urllib

# set path to folder containing the INRIX zip files
# loading is much faster if the data is in Azure
folder = ""  # TODO: set folder

# set SQL instance and database containing INRIX objects
server = ""  # TODO: set SQL instance
db = ""  # TODO: set SQL database

# create SQL connection string to INRIX database
connStr = "DRIVER={SQL Server};" + \
          "SERVER=" + server + ";" + \
          "DATABASE=" + db + ";" + \
          "Trusted_Connection=yes;"

conn = pyodbc.connect(connStr)

engine = sqlalchemy.create_engine(
    "mssql+pyodbc:///?odbc_connect=%s" %
    urllib.parse.quote_plus(connStr))
