import os
import urllib

basedir = os.path.abspath(os.path.dirname(__file__))

# Properly encode the connection parameters
params = urllib.parse.quote_plus(
    "DRIVER={ODBC Driver 17 for SQL Server};"
    "SERVER=LAPTOP-2MTR9RTH\\SQLEXPRESS;"
    "DATABASE=file-movers;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

class Config:
    SQLALCHEMY_DATABASE_URI = f"mssql+pyodbc:///?odbc_connect={params}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
