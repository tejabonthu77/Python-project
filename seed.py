"""Insert synthetic demonstration records. Safe to run more than once."""
from db import get_connection

students = [
    ("S101", "Aarav", "A"), ("S102", "Diya", "A"),
    ("S103", "Kiran", "A"), ("S104", "Meera", "B"),
    ("S105", "Arjun", "B"), ("S106", "Sana", "B"),
]
scores = {
    "S101": [88, 91, 79, 85, 90],
    "S102": [76, 82, 73, 80, 78],
    "S103": [45, 52, 38, 61, 49],
    "S104": [95, 89, 93, 91, 96],
    "S105": [32, 41, 28, 36, 39],
    "S106": [67, 74, 70, 63, 72],
}

conn = get_connection()
try:
    cur = conn.cursor()
    for roll, name, section in students:
        cur.execute(
            "INSERT IGNORE INTO students (roll_no,name,section) VALUES (%s,%s,%s)",
            (roll, name, section)
        )
    cur.execute("SELECT subject_id FROM subjects ORDER BY subject_id")
    subject_ids = [row[0] for row in cur.fetchall()]
    cur.execute("SELECT roll_no,student_id FROM students")
    student_ids = dict(cur.fetchall())
    for roll, marks in scores.items():
        for subject_id, score in zip(subject_ids, marks):
            cur.execute("""
                INSERT IGNORE INTO marks (student_id,subject_id,assessment,marks_obtained)
                VALUES (%s,%s,'Internal 1',%s)
            """, (student_ids[roll], subject_id, score))
    conn.commit()
    print("Synthetic sample data inserted.")
finally:
    cur.close()
    conn.close()
