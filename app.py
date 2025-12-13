# app.py
from flask import Flask, render_template, request, redirect, url_for, flash, abort
import sqlite3
from pathlib import Path
import os

app = Flask(__name__)
app.secret_key = 'very-secret-key-for-dev-only'
port = int(os.environ.get("PORT", 5000))

DB_PATH = Path("instance/database.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # доступ по имени колонки
    return conn

def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with get_db() as conn:
        conn.execute('''
            CREATE TABLE IF NOT EXISTS persons (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                first_name TEXT NOT NULL,
                last_name TEXT NOT NULL,
                middle_name TEXT,
                gender TEXT NOT NULL CHECK(gender IN ('male', 'female', 'other'))
            )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    first = request.form.get('first_name', '').strip()
    last = request.form.get('last_name', '').strip()
    middle = request.form.get('middle_name', '').strip()
    gender = request.form.get('gender')

    if not first or not last or not gender:
        flash("Имя, фамилия и пол обязательны!", "error")
        return redirect(url_for('index'))

    with get_db() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO persons (first_name, last_name, middle_name, gender) VALUES (?, ?, ?, ?)",
            (first, last, middle, gender)
        )
        conn.commit()
        flash("Запись успешно добавлена!", "success")
    return redirect(url_for('list_forms'))

@app.route('/forms')
def list_forms():
    with get_db() as conn:
        rows = conn.execute("SELECT * FROM persons ORDER BY id DESC").fetchall()
    return render_template('list.html', persons=rows)

@app.route('/forms/<int:person_id>')
def view_form(person_id):
    with get_db() as conn:
        person = conn.execute("SELECT * FROM persons WHERE id = ?", (person_id,)).fetchone()
    if not person:
        abort(404)
    return render_template('detail.html', person=person)

@app.route('/forms/<int:person_id>/edit', methods=['GET', 'POST'])
def edit_form(person_id):
    with get_db() as conn:
        person = conn.execute("SELECT * FROM persons WHERE id = ?", (person_id,)).fetchone()
    if not person:
        abort(404)

    if request.method == 'POST':
        first = request.form.get('first_name', '').strip()
        last = request.form.get('last_name', '').strip()
        middle = request.form.get('middle_name', '').strip()
        gender = request.form.get('gender')

        if not first or not last or not gender:
            flash("Имя, фамилия и пол обязательны!", "error")
            return render_template('detail.html', person=person, edit_mode=True)

        with get_db() as conn:
            conn.execute(
                "UPDATE persons SET first_name = ?, last_name = ?, middle_name = ?, gender = ? WHERE id = ?",
                (first, last, middle, gender, person_id)
            )
            conn.commit()
            flash("Запись обновлена!", "success")
        return redirect(url_for('view_form', person_id=person_id))

    return render_template('detail.html', person=person, edit_mode=True)

@app.route('/forms/<int:person_id>/delete', methods=['POST'])
def delete_form(person_id):
    with get_db() as conn:
        conn.execute("DELETE FROM persons WHERE id = ?", (person_id,))
        conn.commit()
    flash("Запись удалена.", "info")
    return redirect(url_for('list_forms'))

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=port, debug=True)