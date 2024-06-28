# word_taker.py

import os
from docx import Document
from sqlite_utils import Database

def process_file(file_path):
    # Open the Word document
    doc = Document(file_path)
    records = []

    for para in doc.paragraphs:
        if ':' in para.text:
            student_id, note = para.text.split(':', 1)
            student_id = student_id.strip()
            note = note.strip()
            records.append((student_id, note))
    
    return records

def create_students_table(db):
    # Create the table if it does not exist
    try:
        db['students'].create({
            'student_id': int,
            'student_note': str
        }, pk='student_id', if_not_exists=True)
    except Exception as e:
        print(f"Error creating students table: {e}")

def insert_into_db(records):
    # Connect to the existing SQLite database
    db_path = r'C:\Users\Noah\Downloads\trial\students.db'  # Adjust the path to your database
    db = Database(db_path)

    create_students_table(db)

    inserted_records = []
    for student_id, note in records:
        try:
            db['students'].insert({
                'student_id': int(student_id),
                'student_note': note
            })
            inserted_records.append((student_id, note))
        except Exception as e:
            print(f"Error inserting record into students table: {e}")
    
    return inserted_records
