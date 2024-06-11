from flask import Flask, g, jsonify, render_template
import sqlite3
import os

app = Flask (__name__)

DATABASE_URL = 'https://drive.google.com/uc?export=download&id=1vImNtUtb61c6n7QMPLqO6MzUrPX7vPyT'
DATABASE_PATH = 'database.db'

def download_database():
    if not os.path.exists(DATABASE_PATH):
        print("Downloading database file...")
        response = requests.get(DATABASE_URL, stream=True)
        with open(DATABASE_PATH, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print("Database downloaded successfully.")

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

@app.route("/")
def home ():
    return "Hello World, from Flask!"
@app.route("/tables")
def get_all_tables():
    db = get_db()
    cursor = db.cursor()

    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    all_data = {}
    for table_name in tables:
        table_name = table_name[0]  # Extract the table name from the tuple
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [column[1] for column in cursor.fetchall()]

        # Prepare data for JSON
        table_data = []
        for row in rows:
            row_data = {columns[i]: row[i] for i in range(len(columns))}
            table_data.append(row_data)
        
        all_data[table_name] = table_data

    return jsonify(all_data)

@app.route("/show-tables")
def show_tables():
    db = get_db()
    cursor = db.cursor()

    # Get the names of all tables in the database
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()

    all_data = {}
    for table_name in tables:
        table_name = table_name[0]  # Extract the table name from the tuple
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()

        # Get column names
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = [column[1] for column in cursor.fetchall()]

        # Prepare data for rendering in template
        table_data = []
        for row in rows:
            row_data = {columns[i]: row[i] for i in range(len(columns))}
            table_data.append(row_data)
        
        all_data[table_name] = table_data

    return render_template('tables.html', tables=all_data)
