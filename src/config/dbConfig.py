from flask_sqlalchemy import SQLAlchemy
from src import app

# D:\Temp\FYP DATA\Git Repos\FYP_BACKEND
app.config['SQL_DATABASE_URI'] = 'sqlite;////mnt/d/Temp/my_db.db'

db = SQLAlchemy(app)