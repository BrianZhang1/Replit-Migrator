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
        self.create_tables()


    def create_tables(self):
        """
        Creates the projects and chat_history tables if they doesn't exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY,
                name TEXT,
                path TEXT,
                link TEXT,
                last_modified TEXT,
                size TEXT
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT
            );
        ''')
        self.conn.commit()


    def write_projects(self, projects):
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
                INSERT INTO projects (name, path, link, last_modified, size)
                VALUES (?, ?, ?, ?, ?);
            ''', (name, project_data['path'], project_data['link'], project_data['last_modified'], project_data['size']))
        self.conn.commit()


    def read_projects(self):
        """
        Reads project data from the projects table.

        Returns:
            dict: A dictionary containing project data.
        """
        self.cursor.execute('SELECT * FROM projects;')
        rows = self.cursor.fetchall()
        projects = {}
        for row in rows:
            id, name, path, link, last_modified, size = row
            projects[name] = {'path': path, 'link': link, 'last_modified': last_modified, 'size': size}
        return projects


    def write_chat_history(self, chat_history):
        """
        Writes chat history data to the chat_history table.

        Args:
            chat_history (list): A list containing chat history data.
        """
        # Delete all rows from the chat_history table.
        self.cursor.execute('DELETE FROM chat_history')

        # Insert new rows into the chat_history table.
        for message in chat_history:
            self.cursor.execute('''
                INSERT INTO chat_history (role, content)
                VALUES (?, ?);
            ''', (message['role'], message['content']))
        self.conn.commit()
    

    def read_chat_history(self):
        """
        Reads chat history data from the chat_history table.

        Returns:
            list: A list containing chat history data.
        """
        self.cursor.execute('SELECT * FROM chat_history;')
        rows = self.cursor.fetchall()
        chat_history = []
        for row in rows:
            id, role, content = row
            chat_history.append({'role': role, 'content': content})
        return chat_history
