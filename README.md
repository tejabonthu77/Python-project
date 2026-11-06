# Student Performance Analysis System

A beginner-friendly Flask + MySQL project for maintaining student profiles, subjects and marks, then analysing academic performance with Pandas, NumPy and Matplotlib.

## 1. Requirements
- Python 3.10 or newer
- Visual Studio Code
- MySQL Server and MySQL Workbench (or another MySQL client)

## 2. Open in VS Code
1. Extract the ZIP file.
2. Open VS Code → File → Open Folder → select `student_performance_analysis_system`.
3. Open Terminal → New Terminal.

## 3. Create virtual environment and install packages
Windows:
```powershell
py -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```
If PowerShell blocks activation, run:
```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.venv\Scripts\activate
```

## 4. Create MySQL database
1. Start MySQL Server.
2. Open MySQL Workbench and connect to your local server.
3. Open `schema.sql`, click the lightning bolt (Execute).
4. This creates the database, three tables and five sample subjects.

## 5. Configure database connection
1. Copy `.env.example` and rename the copy to `.env` (same project folder).
2. Open `.env`.
3. Set `DB_USER` and `DB_PASSWORD` to your local MySQL username and password.
4. Keep `DB_NAME=student_performance_db`.
5. Never upload `.env` or share your database password.

## 6. Add sample data
In VS Code terminal:
```powershell
python seed.py
```
This inserts synthetic sample students and marks. It is safe to run again.

## 7. Run the application
```powershell
python app.py
```
Open the local address printed in the terminal, usually `http://127.0.0.1:5000`.

## Main pages
- `/` Dashboard
- `/students` Add, view, update and delete students
- `/subjects` View and add subjects
- `/marks` Enter and delete marks
- `/reports` Student and subject analysis reports
- `/api/health` Database health check
- `/api/students` GET and POST student API
- `/api/summary` Dashboard summary JSON

## Analysis rules used
- Assessment percentage = (marks obtained / maximum marks) × 100.
- A mark record passes when marks obtained >= that subject's pass marks.
- Student average percentage = mean of the student's recorded assessment percentages.
- Dashboard class average = mean of student average percentages.
- Grade bands: A+ >= 90, A >= 80, B >= 70, C >= 60, D >= 40, F < 40.
- “Needs support” is a project reporting flag for average percentage below 40; it is not a permanent label about a student.
- Subject average chart displays the mean marks recorded for each subject. Interpret it with the subject maximum marks in mind.

## Charts
Three charts are generated from MySQL records and saved under `static/charts/`:
1. Average marks by subject
2. Pass/fail assessment records
3. Distribution of assessment percentages

## Troubleshooting
- `Access denied`: check DB_USER and DB_PASSWORD in `.env`.
- `Unknown database`: execute `schema.sql` in MySQL Workbench.
- `Can't connect`: make sure MySQL Server service is running and DB_HOST/DB_PORT are correct.
- `No module named ...`: activate `.venv` and run `pip install -r requirements.txt`.

## Limitations
This is an educational mini project using synthetic sample data. It has no login/role system and is not an official institutional grading platform. The current student summary averages recorded assessment percentages; it does not assume unrecorded assessments are zero.
