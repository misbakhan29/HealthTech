from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import os
from datetime import date

app = Flask(__name__)
app.secret_key = "your_secret_key_here"

# Database path
DB_PATH = os.path.join(os.path.dirname(__file__), 'database', 'health.db')

# Database connection helper
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        user = conn.execute('SELECT id FROM users WHERE email=? AND password=?',
                            (email, password)).fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            flash("Login successful!", "success")
            return redirect(url_for('dashboard'))
        else:
            flash("Invalid Email or Password!", "danger")

    return render_template('login.html')

# Register route
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        existing_user = conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone()

        if existing_user:
            conn.close()
            flash("Email already registered!", "danger")
            return render_template('register.html')

        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                     (username, email, password))
        conn.commit()
        conn.close()
        flash("Registration successful! Please login.", "success")
        return redirect(url_for('login'))

    return render_template('register.html')

# Dashboard route

def get_db_connection():
    db_path = os.path.join(os.path.dirname(__file__), 'database', 'health.db')
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn

# 🟦 Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    total_habits = conn.execute('SELECT COUNT(*) FROM habits WHERE user_id = ?', (session['user_id'],)).fetchone()[0]

    today = date.today().isoformat()
    completed_today = conn.execute('''
        SELECT COUNT(*) FROM habit_completions
        WHERE date = ? AND status = 'Done'
        AND habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    ''', (today, session['user_id'])).fetchone()[0]

    # Calculate weekly average (past 7 days)
    week_data = conn.execute('''
        SELECT COUNT(*) FROM habit_completions
        WHERE date >= date('now', '-6 days') AND status = 'Done'
        AND habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    ''', (session['user_id'],)).fetchone()[0]

    conn.close()

    weekly_average = round((week_data / (total_habits * 7)) * 100, 2) if total_habits else 0

    return render_template('dashboard.html',
                           total_habits=total_habits,
                           completed_today=completed_today,
                           weekly_average=weekly_average)
@app.route('/dashboard_stats')
def dashboard_stats():
    if 'user_id' not in session:
        return {"total_habits": 0, "completed_today": 0, "weekly_average": 0}

    conn = get_db_connection()
    user_id = session['user_id']
    today = date.today().isoformat()

    total_habits = conn.execute('SELECT COUNT(*) FROM habits WHERE user_id = ?', (user_id,)).fetchone()[0]
    completed_today = conn.execute('''
        SELECT COUNT(*) FROM habit_completions
        WHERE date = ? AND status = 'Done'
        AND habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    ''', (today, user_id)).fetchone()[0]
    week_data = conn.execute('''
        SELECT COUNT(*) FROM habit_completions
        WHERE date >= date('now', '-6 days') AND status = 'Done'
        AND habit_id IN (SELECT id FROM habits WHERE user_id = ?)
    ''', (user_id,)).fetchone()[0]
    conn.close()

    weekly_average = round((week_data / (total_habits * 7)) * 100, 2) if total_habits else 0

    return {
        "total_habits": total_habits,
        "completed_today": completed_today,
        "weekly_average": weekly_average}

# Habits page
@app.route('/habits')
def habits_page():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    conn = get_db_connection()
    today = date.today().isoformat()

    # Get all habits of the user
    habits = conn.execute('SELECT id, habit FROM habits WHERE user_id=?', (session['user_id'],)).fetchall()

    # Make sure there is a status for today
    for h in habits:
        conn.execute('INSERT OR IGNORE INTO habit_completions (habit_id, date, status) VALUES (?, ?, ?)',
                     (h['id'], today, 'Pending'))
    conn.commit()

    # Get habits with today's status
    habit_rows = conn.execute('''
        SELECT h.id, h.habit, hc.status
        FROM habits h
        JOIN habit_completions hc ON h.id = hc.habit_id
        WHERE h.user_id=? AND hc.date=?
    ''', (session['user_id'], today)).fetchall()
    conn.close()

    return render_template('habits.html', habits=habit_rows)

# Add habit (works with normal HTML form)
@app.route('/add_habit', methods=['POST'])
def add_habit():
    if 'user_id' not in session:
        flash("Please login first!", "danger")
        return redirect(url_for('login'))

    habit = request.form.get('habit')  # Use form data
    if not habit:
        flash("Habit name is required!", "danger")
        return redirect(url_for('habits_page'))

    conn = get_db_connection()
    conn.execute('INSERT INTO habits (user_id, habit) VALUES (?, ?)', (session['user_id'], habit))
    conn.commit()
    conn.close()

    flash(f"Habit '{habit}' added successfully!", "success")
    return redirect(url_for('habits_page'))

# Mark habit as done
from datetime import date
from flask import redirect, url_for, flash, session

@app.route('/mark_done/<int:habit_id>', methods=['POST'])
def mark_done(habit_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    today = date.today().isoformat()
    conn = get_db_connection()

    # Insert completion for today if not already done
    conn.execute("""
        INSERT OR REPLACE INTO habit_completions (habit_id, date, status)
        VALUES (?, ?, 'Done')
    """, (habit_id, today))
    conn.commit()
    conn.close()

    flash("✅ Habit marked as done!", "success")
    return redirect(url_for('habits_page'))
# Weekly report
@app.route('/weekly_report')
def weekly_report():
    if 'user_id' not in session:
        return []

    import datetime
    conn = get_db_connection()
    user_id = session['user_id']
    cursor = conn.cursor()

    cursor.execute('''
        SELECT hc.date,
               SUM(CASE WHEN hc.status='Done' THEN 1 ELSE 0 END) AS done_count,
               COUNT(hc.id) AS total_count
        FROM habit_completions hc
        JOIN habits h ON h.id=hc.habit_id
        WHERE h.user_id=? AND hc.date >= DATE('now', '-6 days')
        GROUP BY hc.date
        ORDER BY hc.date
    ''', (user_id,))
    rows = cursor.fetchall()
    conn.close()

    data_dict = {r[0]: {'done': r[1], 'total': r[2]} for r in rows}
    today = datetime.date.today()
    report = []
    for i in range(6, -1, -1):
        d = today - datetime.timedelta(days=i)
        d_str = d.isoformat()
        day_name = d.strftime("%a")
        if d_str in data_dict:
            done = data_dict[d_str]['done']
            total = data_dict[d_str]['total']
            completion = (done / total) * 100 if total else 0
        else:
            completion = 0
        report.append({"day": day_name, "completion": round(completion, 2)})
    return report

# Home route
@app.route('/')
def home():
    if 'user_id' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

# Logout
@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
