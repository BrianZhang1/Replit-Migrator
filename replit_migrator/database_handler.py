import sqlite3

class DatabaseHandler:
    """
    A class that handles data operations for projects.

    Attributes:
        db_path (str): The path to the SQLite database file.
        conn (sqlite3.Connection): The connection to the database.
        cursor (sqlite3.Cursor): The cursor for executing SQL statements.
    """


    def __init__(self, db_path):
        """
        Initializes a new instance of the DataHandler class.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_table()


    def create_table(self):
        """
        Creates the projects table if it doesn't exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                path TEXT,
                link TEXT
            )
        ''')
        self.conn.commit()


    def write(self, projects):
        """
        Writes project data to the projects table.

        Args:
            projects (dict): A dictionary containing project data.
        """
        # Delete all rows from the projects table.
        self.cursor.execute('DELETE FROM projects')

        # Insert new rows into the projects table.
        for name, project_data in projects.items():
            self.cursor.execute('''
                INSERT INTO projects (name, path, link)
                VALUES (?, ?, ?)
            ''', (name, project_data['path'], project_data['link']))
        self.conn.commit()


    def read(self):
        """
        Reads project data from the projects table.

        Returns:
            dict: A dictionary containing project data.
        """
        self.cursor.execute('SELECT name, path, link FROM projects')
        rows = self.cursor.fetchall()
        projects = {}
        for row in rows:
            name, path, link = row
            projects[name] = {'path': path, 'link': link}
        return projects
