import pandas as pd
import numpy as np
from db import get_connection


def load_data():
    conn = get_connection()
    try:
        query = """
            SELECT s.student_id,s.roll_no,s.name,s.section,
                   sub.subject_id,sub.subject_name,sub.max_marks,sub.pass_marks,
                   m.assessment,m.marks_obtained
            FROM marks m
            JOIN students s ON m.student_id=s.student_id
            JOIN subjects sub ON m.subject_id=sub.subject_id
        """
        return pd.read_sql(query, conn)
    finally:
        conn.close()


def get_dashboard_data():
    df = load_data()
    student_count = int(df["student_id"].nunique()) if not df.empty else 0
    subject_count = int(df["subject_id"].nunique()) if not df.empty else 0
    if df.empty:
        return {
            "student_count": student_count, "subject_count": subject_count,
            "record_count": 0, "class_average": 0, "pass_rate": 0,
            "topper": "No data yet", "low_performers": 0,
            "subject_averages": [], "pass_fail": {"Pass": 0, "Fail": 0}
        }

    # Calculate percentage for each assessment record.
    df["percentage"] = (df["marks_obtained"] / df["max_marks"]) * 100
    df["passed"] = df["marks_obtained"] >= df["pass_marks"]

    # Average each student's percentage across their recorded assessments.
    student_summary = df.groupby(["student_id", "roll_no", "name", "section"], as_index=False).agg(
        average_percentage=("percentage", "mean")
    )
    class_average = float(np.mean(student_summary["average_percentage"]))
    topper_row = student_summary.sort_values("average_percentage", ascending=False).iloc[0]
    low_count = int((student_summary["average_percentage"] < 40).sum())

    subject_summary = df.groupby("subject_name", as_index=False).agg(
        average_marks=("marks_obtained", "mean"),
        pass_count=("passed", "sum"),
        record_count=("passed", "count")
    )
    subject_summary["pass_percentage"] = (
        subject_summary["pass_count"] / subject_summary["record_count"] * 100
    )
    passed = int(df["passed"].sum())
    failed = int((~df["passed"]).sum())

    return {
        "student_count": student_count,
        "subject_count": subject_count,
        "record_count": int(len(df)),
        "class_average": round(class_average, 2),
        "pass_rate": round(passed / len(df) * 100, 2),
        "topper": f'{topper_row["name"]} ({topper_row["roll_no"]})',
        "low_performers": low_count,
        "subject_averages": [
            {"subject": r.subject_name, "average": round(float(r.average_marks), 2),
             "pass_percentage": round(float(r.pass_percentage), 2)}
            for r in subject_summary.itertuples()
        ],
        "pass_fail": {"Pass": passed, "Fail": failed}
    }


def get_student_report():
    df = load_data()
    if df.empty:
        return []
    df["percentage"] = df["marks_obtained"] / df["max_marks"] * 100
    grouped = df.groupby(["student_id", "roll_no", "name", "section"], as_index=False).agg(
        total_marks=("marks_obtained", "sum"),
        max_total=("max_marks", "sum"),
        average_percentage=("percentage", "mean"),
        assessments=("marks_obtained", "count")
    )
    grouped["grade"] = grouped["average_percentage"].apply(
        lambda x: "A+" if x >= 90 else "A" if x >= 80 else "B" if x >= 70
        else "C" if x >= 60 else "D" if x >= 40 else "F"
    )
    grouped["status"] = grouped["average_percentage"].apply(lambda x: "Pass" if x >= 40 else "Needs support")
    return [
        {**r, "total_marks": round(float(r["total_marks"]), 1),
         "average_percentage": round(float(r["average_percentage"]), 1)}
        for r in grouped.to_dict("records")
    ]


def get_subject_report():
    df = load_data()
    if df.empty:
        return []
    df["passed"] = df["marks_obtained"] >= df["pass_marks"]
    grouped = df.groupby("subject_name").agg(
        average=("marks_obtained", "mean"),
        median=("marks_obtained", lambda x: np.median(x)),
        minimum=("marks_obtained", "min"),
        maximum=("marks_obtained", "max"),
        pass_rate=("passed", lambda x: x.mean() * 100)
    ).reset_index()
    return [
        {"subject": r.subject_name, "average": round(float(r.average), 2),
         "median": round(float(r.median), 2), "minimum": float(r.minimum),
         "maximum": float(r.maximum), "pass_rate": round(float(r.pass_rate), 2)}
        for r in grouped.itertuples()
    ]
