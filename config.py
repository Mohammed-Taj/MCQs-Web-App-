class Config:
    SECRET_KEY =  'change-this-secret'
    SQLALCHEMY_DATABASE_URI ="mssql+pyodbc://localhost/QuizDB?driver=ODBC+Driver+17+for+SQL+Server&trusted_connection=yes"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
