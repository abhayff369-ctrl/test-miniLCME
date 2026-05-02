from flask import Flask, jsonify
import sqlite3, os, csv

app = Flask(__name__)

CSV_FILE = "data.csv"
DB_FILE = "data.db"

def create_db_from_csv():
    print("Creating SQLite DB safely (no pandas)...")
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS people (
            name TEXT,
            fathersName TEXT,
            phoneNumber TEXT,
            otherNumber TEXT,
            passportNumber TEXT,
            aadharNumber TEXT,
            age TEXT,
            gender TEXT,
            address TEXT,
            district TEXT,
            pincode TEXT,
            state TEXT,
            town TEXT
        )
    """)
    conn.commit()

    with open(CSV_FILE, "r", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader, start=1):
            values = [row.get(h, "") for h in [
                "name", "fathersName", "phoneNumber", "otherNumber",
                "passportNumber", "aadharNumber", "age", "gender",
                "address", "district", "pincode", "state", "town"
            ]]
            rows.append(values)
            if len(rows) >= 1000:
                cur.executemany("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
                conn.commit()
                rows.clear()
                print(f"Inserted {i} rows...")
        if rows:
            cur.executemany("INSERT INTO people VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
            conn.commit()

    conn.close()
    print("Database created successfully (safe mode).")

def query_db(field, value):
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM people WHERE {field}=?", (value,))
    row = cur.fetchone()
    conn.close()
    if row:
        return dict(row)
    return None

if not os.path.exists(DB_FILE):
    if not os.path.exists(CSV_FILE):
        print("Error: data.csv not found!")
        exit()
    create_db_from_csv()
else:
    print("Database already exists, skipping creation.")

@app.route("/aadhar/<aadhar>")
def aadhar_info(aadhar):
    data = query_db("aadharNumber", aadhar)
    return jsonify(data or {"error": "Aadhar not found"})

@app.route("/phonenumber/<num>")
def phone_info(num):
    data = query_db("phoneNumber", num)
    return jsonify(data or {"error": "Phone number not found"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
