from sqlite_utils import Database
import sqlite_utils.db
import sqlite3

class StudentDB:
    def __init__(self, db_name="students.db"):
        try:
            self.db = Database(db_name)
            self.create_table()
        except sqlite3.Error as e:
            print(f"Error connecting to the database: {e}")

    def create_table(self):
        try:
            self.db['students'].create({
                'student_id': int,
                'student_note': str
            }, pk='student_id')
        except sqlite3.Error as e:
            print(f"Error creating table: {e}")

    def add_student(self, student_id, student_note):
        try:
            self.db['students'].insert({
                'student_id': student_id,
                'student_note': student_note
            })
        except sqlite3.Error as e:
            print(f"Error adding student: {e}")

    def get_student_data(self, student_id):
        try:
            student_data = self.db['students'].get(student_id)
            if student_data is None:
                print("Student not found.")
                return None
            else:
                return student_data
        except sqlite_utils.db.NotFoundError:
            print("Error retrieving student data: Student not found")
            return None

    def delete_student(self, student_id):
        try:
            self.db['students'].delete(student_id)
        except sqlite_utils.db.NotFoundError:
            print("Error deleting student: Student not found")
            return False
        return True

