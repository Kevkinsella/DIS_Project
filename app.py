from flask import Flask, render_template, request, jsonify
import random
import string
import psycopg2
from datetime import datetime, timedelta

app = Flask(__name__)

DB_HOST = 'localhost'
DB_PORT = '5432'
DB_NAME = 'TINProject'
DB_USER = 'testuser'
DB_PASS = '123'

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

def convert_format_to_pattern(format_str):
    format_str = format_str.upper()
    pattern = ""
    for char in format_str:
        if char in "0123456789X":
            pattern += "#"
        elif char in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            pattern += "A"
        elif char in "-.() /":
            pattern += char
        else:
            pattern += "?"
    return pattern

def generate_tin(format_str):
    tin = ""
    for char in format_str:
        if char == '#':
            tin += str(random.randint(0, 9))
        elif char == 'A':
            tin += random.choice(string.ascii_uppercase)
        elif char == '?':
            tin += random.choice(string.ascii_uppercase + string.digits)
        else:
            tin += char
    return tin

def generate_cpr():
    start = datetime(1900, 1, 1)
    end = datetime.today()
    delta = end - start
    birth_date = start + timedelta(days=random.randint(0, delta.days))
    return birth_date.strftime("%d%m%y") + "".join(random.choices(string.digits, k=4))

def is_valid_cpr(cpr):
    try:
        datetime.strptime(cpr[:6], "%d%m%y")
        return len(cpr) == 10 and cpr.isdigit()
    except:
        return False

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute('SELECT "code", "example" FROM "Countries" ORDER BY "code" ASC')
    countries = cur.fetchall()
    tin_formats = {code: convert_format_to_pattern(example) for code, example in countries}
    tin_examples = {code: example for code, example in countries}

    cur.execute('SELECT "EmployerID", "Name" FROM "Employers" ORDER BY "Name" ASC')
    employers = cur.fetchall()
    employers = [{'EmployerID': eid, 'Name': name} for eid, name in employers]

    cur.close()
    conn.close()

    return render_template("index.html",
                           countries=tin_formats.keys(),
                           tin_formats=tin_formats,
                           employers=employers,
                           tin_examples=tin_examples)

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    name = data.get("name", "").strip()
    country = data.get("country")
    cpr = data.get("cpr", "").strip()
    employer = data.get("employer", "").strip()
    tin_type = data.get("tin_type", "Auto").strip()
    start_date = data.get("start_date") or datetime.today().strftime("%Y-%m-%d")
    end_date = data.get("end_date", "").strip() or None

    if not name or not country:
        return jsonify({"error": "Ugyldige input."})

    if cpr and not is_valid_cpr(cpr):
        return jsonify({"error": "Ugyldigt CPR-nummer."})

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT "example" FROM "Countries" WHERE "code" = %s', (country,))
    row = cur.fetchone()
    if not row:
        return jsonify({"error": "Ukendt land."})
    format_str = convert_format_to_pattern(row[0])
    tin = generate_tin(format_str)

    cur.execute('SELECT "EmployerID" FROM "Employers" WHERE LOWER("Name") = LOWER(%s)', (employer,))
    result = cur.fetchone()

    if result:
        employer_id = result[0]
    else:
        cur.execute(
            'INSERT INTO "Employers" ("Name", "Country_ID") VALUES (%s, %s) RETURNING "EmployerID"',
            (employer, country)
        )
        employer_id = cur.fetchone()[0]
        conn.commit()

    name_parts = name.split()
    first_name = name_parts[0]
    surname = " ".join(name_parts[1:]) if len(name_parts) > 1 else ""

    status = "Aktiv"
    if end_date:
        try:
            if datetime.strptime(end_date, "%Y-%m-%d").date() < datetime.today().date():
                status = "Inaktiv"
        except:
            status = "Ukendt"

    generated_cpr = cpr if cpr else generate_cpr()

    cur.execute("""
        INSERT INTO "People" (
            "CPR_nr", "F_name", "Surname", "EmployerID", "Country_ID",
            "TIN_value", "TIN_type", "Start_Date", "End_Date", "TIN_status"
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        generated_cpr,
        first_name, surname, employer_id, country, tin, tin_type, start_date, end_date, status
    ))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"name": name, "tin": tin})

@app.route("/employer-lookup", methods=["POST"])
def employer_lookup():
    data = request.json
    name = data.get("name", "").strip()

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('SELECT "EmployerID" FROM "Employers" WHERE LOWER("Name") = LOWER(%s)', (name,))
    result = cur.fetchone()

    if not result:
        cur.close()
        conn.close()
        return jsonify({"error": "Virksomheden blev ikke fundet."})

    employer_id = result[0]

    cur.execute('''
        SELECT "F_name", "Surname", "TIN_value", "Start_Date", "End_Date"
        FROM "People"
        WHERE "EmployerID" = %s
    ''', (employer_id,))

    employees = []
    today = datetime.today().date()

    for row in cur.fetchall():
        fname, sname, tin, start_date, end_date = row
        if end_date and end_date < today:
            status = "Inaktiv"
        else:
            status = "Aktiv"

        employees.append({
            "F_name": fname,
            "Surname": sname,
            "TIN_value": tin,
            "Status": status
        })

    cur.close()
    conn.close()

    return jsonify({"people": employees})

@app.route("/pension-lookup", methods=["POST"])
def pension_lookup():
    data = request.json
    tin = data.get("tin", "").strip()
    country = data.get("country", "").strip()

    if not tin or not country:
        return jsonify({"error": "Både land og TIN skal udfyldes."})

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute('''
        SELECT "F_name", "Surname", "TIN_type", "TIN_status", "Country_ID"
        FROM "People"
        WHERE "TIN_value" = %s AND "Country_ID" = %s
    ''', (tin, country))

    result = cur.fetchone()
    cur.close()
    conn.close()

    if not result:
        return jsonify({"error": "Ingen person fundet med dette TIN og land."})

    fname, sname, tin_type, tin_status, country_id = result

    return jsonify({
        "F_name": fname,
        "Surname": sname,
        "TIN_type": tin_type,
        "TIN_status": tin_status,
        "Country_ID": country_id
    })

@app.route("/save-score", methods=["POST"])
def save_score():
    data = request.json
    name = data.get("name", "Ukendt")
    score = data.get("score", 0)

    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'INSERT INTO "Highscores" ("Timestamp", "Name", "Score") VALUES (%s, %s, %s)',
        (datetime.now(), name, score)
    )
    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Highscore gemt!"})

@app.route("/get-highscores", methods=["GET"])
def get_highscores():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute(
        'SELECT "Name", "Score" FROM "Highscores" ORDER BY "Score" DESC LIMIT 5'
    )
    highscores = cur.fetchall()
    cur.close()
    conn.close()

    return jsonify({"highscores": highscores})

if __name__ == "__main__":
    app.run(debug=True)
