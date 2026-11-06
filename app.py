from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from mysql.connector import Error, IntegrityError
from db import get_connection
from analysis import get_dashboard_data, get_student_report, get_subject_report
from charts import generate_charts
from config import Config

app = Flask(__name__)
app.config.from_object(Config)


def fetch_all(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor(dictionary=True)
        cur.execute(query, params)
        return cur.fetchall()
    finally:
        cur.close()
        conn.close()


def execute(query, params=()):
    conn = get_connection()
    try:
        cur = conn.cursor()
        cur.execute(query, params)
        conn.commit()
        return cur.lastrowid
    finally:
        cur.close()
        conn.close()


@app.route("/")
def dashboard():
    try:
        data = get_dashboard_data()
        generate_charts()
        return render_template("dashboard.html", data=data)
    except Error as exc:
        return render_template("setup_error.html", error=str(exc))


@app.route("/students")
def students():
    rows = fetch_all("""
        SELECT s.student_id, s.roll_no, s.name, s.section,
               COUNT(m.mark_id) AS assessments
        FROM students s LEFT JOIN marks m ON s.student_id=m.student_id
        GROUP BY s.student_id, s.roll_no, s.name, s.section
        ORDER BY s.roll_no
    """)
    return render_template("students.html", students=rows)


@app.route("/students/add", methods=["POST"])
def add_student():
    roll = request.form.get("roll_no", "").strip()
    name = request.form.get("name", "").strip()
    section = request.form.get("section", "").strip().upper()
    if not roll or not name or not section:
        flash("Please fill in all student fields.", "error")
    elif len(name) > 100 or len(roll) > 30 or len(section) > 10:
        flash("One or more fields are too long.", "error")
    else:
        try:
            execute("INSERT INTO students (roll_no,name,section) VALUES (%s,%s,%s)",
                    (roll, name, section))
            flash("Student added successfully.", "success")
        except IntegrityError:
            flash("That roll number already exists.", "error")
        except Error as exc:
            flash(f"Database error: {exc}", "error")
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/update", methods=["POST"])
def update_student(student_id):
    roll = request.form.get("roll_no", "").strip()
    name = request.form.get("name", "").strip()
    section = request.form.get("section", "").strip().upper()
    if not roll or not name or not section:
        flash("All fields are required.", "error")
    else:
        try:
            execute("UPDATE students SET roll_no=%s,name=%s,section=%s WHERE student_id=%s",
                    (roll, name, section, student_id))
            flash("Student updated.", "success")
        except IntegrityError:
            flash("That roll number is already used by another student.", "error")
        except Error as exc:
            flash(f"Database error: {exc}", "error")
    return redirect(url_for("students"))


@app.route("/students/<int:student_id>/delete", methods=["POST"])
def delete_student(student_id):
    try:
        execute("DELETE FROM students WHERE student_id=%s", (student_id,))
        flash("Student and related marks deleted.", "success")
    except Error as exc:
        flash(f"Could not delete student: {exc}", "error")
    return redirect(url_for("students"))


@app.route("/subjects")
def subjects():
    rows = fetch_all("SELECT * FROM subjects ORDER BY subject_name")
    return render_template("subjects.html", subjects=rows)


@app.route("/subjects/add", methods=["POST"])
def add_subject():
    name = request.form.get("subject_name", "").strip()
    try:
        maximum = int(request.form.get("max_marks", "100"))
        passing = int(request.form.get("pass_marks", "40"))
        if not name or maximum <= 0 or passing < 0 or passing > maximum:
            raise ValueError
        execute("INSERT INTO subjects (subject_name,max_marks,pass_marks) VALUES (%s,%s,%s)",
                (name, maximum, passing))
        flash("Subject added.", "success")
    except ValueError:
        flash("Enter a subject name, positive maximum marks and valid pass marks.", "error")
    except IntegrityError:
        flash("That subject already exists.", "error")
    except Error as exc:
        flash(f"Database error: {exc}", "error")
    return redirect(url_for("subjects"))


@app.route("/marks")
def marks():
    students_list = fetch_all("SELECT student_id,roll_no,name,section FROM students ORDER BY roll_no")
    subjects_list = fetch_all("SELECT subject_id,subject_name,max_marks FROM subjects ORDER BY subject_name")
    rows = fetch_all("""
        SELECT m.mark_id,s.roll_no,s.name,s.section,
               sub.subject_name,m.assessment,m.marks_obtained,sub.max_marks
        FROM marks m JOIN students s ON m.student_id=s.student_id
        JOIN subjects sub ON m.subject_id=sub.subject_id
        ORDER BY m.mark_id DESC
    """)
    return render_template("marks.html", students=students_list, subjects=subjects_list, marks=rows)


@app.route("/marks/add", methods=["POST"])
def add_mark():
    try:
        student_id = int(request.form["student_id"])
        subject_id = int(request.form["subject_id"])
        assessment = request.form.get("assessment", "Internal 1").strip()
        score = float(request.form["marks_obtained"])
        subject = fetch_all("SELECT max_marks FROM subjects WHERE subject_id=%s", (subject_id,))
        if not subject:
            raise ValueError("Choose a valid subject.")
        if score < 0 or score > float(subject[0]["max_marks"]):
            raise ValueError(f"Marks must be between 0 and {subject[0]['max_marks']}.")
        if not assessment:
            raise ValueError("Assessment name is required.")
        execute("""INSERT INTO marks (student_id,subject_id,assessment,marks_obtained)
                   VALUES (%s,%s,%s,%s)""", (student_id, subject_id, assessment, score))
        flash("Marks saved successfully.", "success")
    except (ValueError, KeyError):
        flash("Invalid input. Check the student, subject and marks.", "error")
    except Error as exc:
        flash(f"Database error: {exc}", "error")
    return redirect(url_for("marks"))


@app.route("/marks/<int:mark_id>/delete", methods=["POST"])
def delete_mark(mark_id):
    try:
        execute("DELETE FROM marks WHERE mark_id=%s", (mark_id,))
        flash("Mark record deleted.", "success")
    except Error as exc:
        flash(f"Database error: {exc}", "error")
    return redirect(url_for("marks"))


@app.route("/reports")
def reports():
    try:
        generate_charts()
        students_report = get_student_report()
        subjects_report = get_subject_report()
        return render_template("reports.html", students=students_report, subjects=subjects_report)
    except Error as exc:
        flash(f"Could not create report: {exc}", "error")
        return redirect(url_for("dashboard"))


@app.route("/api/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok", "database": "connected"})
    except Error as exc:
        return jsonify({"status": "error", "database": "disconnected", "message": str(exc)}), 500


@app.route("/api/students", methods=["GET", "POST"])
def api_students():
    if request.method == "GET":
        return jsonify(fetch_all("SELECT * FROM students ORDER BY roll_no"))
    payload = request.get_json(silent=True) or {}
    roll, name, section = (str(payload.get(k, "")).strip() for k in ("roll_no", "name", "section"))
    if not all((roll, name, section)):
        return jsonify({"error": "roll_no, name and section are required"}), 400
    try:
        new_id = execute("INSERT INTO students (roll_no,name,section) VALUES (%s,%s,%s)",
                         (roll, name, section.upper()))
        return jsonify({"message": "Student created", "student_id": new_id}), 201
    except IntegrityError:
        return jsonify({"error": "roll_no already exists"}), 409


@app.route("/api/summary")
def api_summary():
    try:
        return jsonify(get_dashboard_data())
    except Error as exc:
        return jsonify({"error": str(exc)}), 500


@app.errorhandler(404)
def not_found(_):
    return render_template("404.html"), 404


if __name__ == "__main__":
    app.run(debug=True)
