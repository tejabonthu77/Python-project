CREATE DATABASE IF NOT EXISTS student_performance_db;
USE student_performance_db;

CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    roll_no VARCHAR(30) NOT NULL UNIQUE,
    name VARCHAR(100) NOT NULL,
    section VARCHAR(10) NOT NULL
);

CREATE TABLE IF NOT EXISTS subjects (
    subject_id INT AUTO_INCREMENT PRIMARY KEY,
    subject_name VARCHAR(100) NOT NULL UNIQUE,
    max_marks DECIMAL(7,2) NOT NULL CHECK (max_marks > 0),
    pass_marks DECIMAL(7,2) NOT NULL CHECK (pass_marks >= 0 AND pass_marks <= max_marks)
);

CREATE TABLE IF NOT EXISTS marks (
    mark_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    subject_id INT NOT NULL,
    assessment VARCHAR(50) NOT NULL,
    marks_obtained DECIMAL(7,2) NOT NULL CHECK (marks_obtained >= 0),
    CONSTRAINT fk_marks_student FOREIGN KEY (student_id)
        REFERENCES students(student_id) ON DELETE CASCADE,
    CONSTRAINT fk_marks_subject FOREIGN KEY (subject_id)
        REFERENCES subjects(subject_id) ON DELETE CASCADE,
    CONSTRAINT uq_student_subject_assessment UNIQUE (student_id, subject_id, assessment)
);

INSERT IGNORE INTO subjects (subject_name, max_marks, pass_marks) VALUES
('Python',100,40),('DBMS',100,40),('Java',100,40),('Mathematics',100,40),('Computer Networks',100,40);
