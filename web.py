from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
import os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'Manish123'  


def setup_database():
    conn = sqlite3.connect("content_generation.db")

    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generated_content (
            user_id TEXT,
            prompt TEXT,
            image_paths TEXT,
            status TEXT,
            generated_at TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id TEXT,
            action TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

setup_database()


def log_user_action(user_id, action):
    conn = sqlite3.connect("content_generation.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO user_logs (user_id, action, timestamp) VALUES (?, ?, ?)",
        (user_id, action, datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    )
    conn.commit()
    conn.close()

def get_user_content(user_id):
    conn = sqlite3.connect("content_generation.db")
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM generated_content WHERE user_id = ?", (user_id,))
    content = cursor.fetchall()
    conn.close()
    return content


@app.route('/')
def home():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def login():
    user_id = request.form['user_id']
    session['user_id'] = user_id
    log_user_action(user_id, "Login attempt")
    return redirect(url_for('dashboard'))


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('home'))

    user_id = session['user_id']
    content = get_user_content(user_id)

    if not content or all(item[3] == "Processing" for item in content):
        log_user_action(user_id, "Viewed dashboard - Content processing")
        return render_template('processing.html', user_id=user_id)

    images_with_prompts = []
    for item in content:
        if item[2] and item[3] == "Completed":
            image_path = item[2].replace('\\', '/')
            images_with_prompts.append({"image_path": url_for('static', filename=image_path), "prompt": item[1]})

    log_user_action(user_id, "Viewed dashboard - Content ready")
    return render_template('dashboard.html', user_id=user_id, images_with_prompts=images_with_prompts)


@app.route('/logout')
def logout():
    user_id = session.pop('user_id', None)
    if user_id:
        log_user_action(user_id, "Logout")
    return redirect(url_for('home'))


if __name__ == "__main__":
    app.run(debug=True)
