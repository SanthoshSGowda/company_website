from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3, os, datetime

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-in-prod")
DB_NAME = "site.db"

def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()
    # users
    cur.execute("""CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )""")
    # services
    cur.execute("""CREATE TABLE IF NOT EXISTS services (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        description TEXT NOT NULL,
        icon TEXT DEFAULT 'bi-lightning-fill'
    )""")
    # team
    cur.execute("""CREATE TABLE IF NOT EXISTS team (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        role TEXT NOT NULL,
        photo_url TEXT
    )""")
    # messages
    cur.execute("""CREATE TABLE IF NOT EXISTS messages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT NOT NULL,
        message TEXT NOT NULL,
        created_at TEXT NOT NULL
    )""")
    conn.commit()

    # seed admin
    cur.execute("SELECT COUNT(*) FROM users")
    if cur.fetchone()[0] == 0:
        cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                    ("admin", generate_password_hash("admin123")))
        conn.commit()

    # seed services
    cur.execute("SELECT COUNT(*) FROM services")
    if cur.fetchone()[0] == 0:
        demo_services = [
            ("Web Development", "Modern, responsive websites and web apps.", "bi-code-slash"),
            ("Cloud & DevOps", "CI/CD, containerization, and scalable infra.", "bi-cloud-arrow-up-fill"),
            ("Data Analytics", "Dashboards, pipelines, and insights.", "bi-bar-chart-fill")
        ]
        cur.executemany("INSERT INTO services (title, description, icon) VALUES (?, ?, ?)", demo_services)
        conn.commit()

    # seed team
    cur.execute("SELECT COUNT(*) FROM team")
    if cur.fetchone()[0] == 0:
        demo_team = [
            ("Aarav Mehta", "santhu", "https://images.unsplash.com/photo-1607746882042-944635dfe10e?w=400"),
            ("Isha Sharma", "santhu", "https://images.unsplash.com/photo-1544005313-94ddf0286df2?w=400"),
            ("Rahul Verma", "DevOps Engineer", "https://images.unsplash.com/photo-1547425260-76bcadfb4f2c?w=400"),
        ]
        cur.executemany("INSERT INTO team (name, role, photo_url) VALUES (?, ?, ?)", demo_team)
        conn.commit()

    conn.close()

def login_required(view):
    from functools import wraps
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("admin_login"))
        return view(*args, **kwargs)
    return wrapped

@app.route("/")
def home():
    conn = get_db()
    services = conn.execute("SELECT * FROM services").fetchall()
    team = conn.execute("SELECT * FROM team LIMIT 3").fetchall()
    conn.close()
    return render_template("home.html", services=services, team=team)

@app.route("/about")
def about():
    conn = get_db()
    team = conn.execute("SELECT * FROM team").fetchall()
    conn.close()
    return render_template("about.html", team=team)

@app.route("/services")
def services():
    conn = get_db()
    services = conn.execute("SELECT * FROM services").fetchall()
    conn.close()
    return render_template("services.html", services=services)

@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        email = request.form.get("email","").strip()
        message = request.form.get("message","").strip()
        if not (name and email and message):
            flash("All fields are required.", "danger")
        else:
            conn = get_db()
            conn.execute("INSERT INTO messages (name,email,message,created_at) VALUES (?,?,?,?)",
                         (name, email, message, datetime.datetime.utcnow().isoformat()))
            conn.commit()
            conn.close()
            flash("Thanks! Your message has been received.", "success")
            return redirect(url_for("contact"))
    return render_template("contact.html")

# -------- Admin --------
@app.route("/admin/login", methods=["GET","POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE username=?", (username,)).fetchone()
        conn.close()
        if user and check_password_hash(user["password_hash"], password):
            session["user_id"] = user["id"]
            session["username"] = username
            return redirect(url_for("admin_dashboard"))
        flash("Invalid credentials", "danger")
    return render_template("admin/login.html")

@app.route("/admin/logout")
def admin_logout():
    session.clear()
    return redirect(url_for("admin_login"))

@app.route("/admin")
@login_required
def admin_dashboard():
    conn = get_db()
    counts = {
        "services": conn.execute("SELECT COUNT(*) FROM services").fetchone()[0],
        "team": conn.execute("SELECT COUNT(*) FROM team").fetchone()[0],
        "messages": conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0],
    }
    conn.close()
    return render_template("admin/dashboard.html", counts=counts)

# Services CRUD
@app.route("/admin/services")
@login_required
def admin_services():
    conn = get_db()
    rows = conn.execute("SELECT * FROM services").fetchall()
    conn.close()
    return render_template("admin/services_list.html", rows=rows)

@app.route("/admin/services/new", methods=["GET","POST"])
@login_required
def admin_services_new():
    if request.method == "POST":
        title = request.form.get("title","").strip()
        description = request.form.get("description","").strip()
        icon = request.form.get("icon","bi-star-fill").strip()
        if not (title and description):
            flash("Title and description are required.", "danger")
        else:
            conn = get_db()
            conn.execute("INSERT INTO services (title, description, icon) VALUES (?,?,?)",
                         (title, description, icon))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_services"))
    return render_template("admin/services_form.html", item=None)

@app.route("/admin/services/<int:item_id>/edit", methods=["GET","POST"])
@login_required
def admin_services_edit(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM services WHERE id=?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return redirect(url_for("admin_services"))
    if request.method == "POST":
        title = request.form.get("title","").strip()
        description = request.form.get("description","").strip()
        icon = request.form.get("icon","bi-star-fill").strip()
        conn.execute("UPDATE services SET title=?, description=?, icon=? WHERE id=?",
                     (title, description, icon, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_services"))
    conn.close()
    return render_template("admin/services_form.html", item=item)

@app.route("/admin/services/<int:item_id>/delete", methods=["POST"])
@login_required
def admin_services_delete(item_id):
    conn = get_db()
    conn.execute("DELETE FROM services WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    flash("Service deleted.", "info")
    return redirect(url_for("admin_services"))

# Team CRUD
@app.route("/admin/team")
@login_required
def admin_team():
    conn = get_db()
    rows = conn.execute("SELECT * FROM team").fetchall()
    conn.close()
    return render_template("admin/team_list.html", rows=rows)

@app.route("/admin/team/new", methods=["GET","POST"])
@login_required
def admin_team_new():
    if request.method == "POST":
        name = request.form.get("name","").strip()
        role = request.form.get("role","").strip()
        photo_url = request.form.get("photo_url","").strip()
        if not (name and role):
            flash("Name and role are required.", "danger")
        else:
            conn = get_db()
            conn.execute("INSERT INTO team (name, role, photo_url) VALUES (?,?,?)",
                         (name, role, photo_url))
            conn.commit()
            conn.close()
            return redirect(url_for("admin_team"))
    return render_template("admin/team_form.html", item=None)

@app.route("/admin/team/<int:item_id>/edit", methods=["GET","POST"])
@login_required
def admin_team_edit(item_id):
    conn = get_db()
    item = conn.execute("SELECT * FROM team WHERE id=?", (item_id,)).fetchone()
    if not item:
        conn.close()
        return redirect(url_for("admin_team"))
    if request.method == "POST":
        name = request.form.get("name","").strip()
        role = request.form.get("role","").strip()
        photo_url = request.form.get("photo_url","").strip()
        conn.execute("UPDATE team SET name=?, role=?, photo_url=? WHERE id=?",
                     (name, role, photo_url, item_id))
        conn.commit()
        conn.close()
        return redirect(url_for("admin_team"))
    conn.close()
    return render_template("admin/team_form.html", item=item)

@app.route("/admin/team/<int:item_id>/delete", methods=["POST"])
@login_required
def admin_team_delete(item_id):
    conn = get_db()
    conn.execute("DELETE FROM team WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    flash("Team member deleted.", "info")
    return redirect(url_for("admin_team"))

# Messages view
@app.route("/admin/messages")
@login_required
def admin_messages():
    conn = get_db()
    rows = conn.execute("SELECT * FROM messages ORDER BY created_at DESC").fetchall()
    conn.close()
    return render_template("admin/messages.html", rows=rows)

if __name__ == "__main__":
    init_db()
    app.run(host="0.0.0.0", port=5000)
