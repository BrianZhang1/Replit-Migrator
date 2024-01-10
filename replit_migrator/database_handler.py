import sqlite3
import requests
import json

class DatabaseHandler:
    """
    A class that handles data operations for projects.

    Attributes:
        db_path (str): The path to the SQLite database file.
        conn (sqlite3.Connection): The connection to the database.
        cursor (sqlite3.Cursor): The cursor for executing SQL statements.
    """


    def __init__(self, db_path, API_ROOT_URL):
        """
        Initializes a new instance of the DataHandler class.

        Args:
            db_path (str): The path to the SQLite database file.
        """
        self.db_path = db_path
        self.API_ROOT_URL = API_ROOT_URL

        self.conn = sqlite3.connect(db_path)
        self.cursor = self.conn.cursor()
        self.create_tables()


    def create_tables(self):
        """
        Creates the projects and chat_history tables if they doesn't exist.
        """
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS migrations (
                id INTEGER PRIMARY KEY,
                date_time TEXT
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY,
                role TEXT,
                content TEXT
            );
        ''')
        # Create logindetails table.
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS login_details (
                id INTEGER PRIMARY KEY,
                username TEXT,
                password TEXT
            );
        ''')
        self.conn.commit()


    def create_migration_table(self, date_time):
        self.cursor.execute('INSERT INTO migrations (date_time) VALUES (?);', (date_time,))
        id = self.cursor.execute('SELECT last_insert_rowid();').fetchone()[0]
        self.cursor.execute(f'''
            CREATE TABLE IF NOT EXISTS projects_{id} (
                id INTEGER PRIMARY KEY,
                name TEXT,
                path TEXT,
                link TEXT,
                last_modified TEXT,
                size TEXT
            );
        ''')
        self.conn.commit()


    def get_migration_tables(self):
        """
        Retrieves the details of all entries in the migrations table and returns them as a list,
        where each entry is a dictionary containing the id and date_time of the migration.
        """
        self.cursor.execute('SELECT * FROM migrations;')
        rows = self.cursor.fetchall()
        migrations = []
        for row in rows:
            id, date_time = row
            migrations.append({'id': id, 'date_time': date_time})
        return migrations


    def write_projects(self, projects, table_id=None, login_details=None):
        """
        Writes project data to the specified projects table.
        If user is logged in, uploads chat history to the Replit Migrator Database Server.
        """

        if table_id is None:
            # If id not specified, use id of the latest migration table created.
            table_id = self.cursor.execute('SELECT id FROM migrations ORDER BY id DESC LIMIT 1;').fetchone()[0]
            

        table_name = f'projects_{table_id}'

        # Delete all rows from the projects table.
        self.cursor.execute(f'DELETE FROM {table_name}')

        # Insert new rows into the projects table.
        for name, project_data in projects.items():
            self.cursor.execute(f'''
                INSERT INTO {table_name} (name, path, link, last_modified, size)
                VALUES (?, ?, ?, ?, ?);
            ''', (name, project_data['path'], project_data['link'], project_data['last_modified'], project_data['size']))
        self.conn.commit()

        # Check if user is logged in.
        if self.check_if_logged_in():
            # User is logged in. Get login details.
            login_details = self.read_login_details()
            # Upload projects to the Replit Migrator Database Server.
            self.upload_database_to_server(login_details['username'], login_details['password'])


    def read_projects(self, table_id=None):
        """
        Reads project data from the specified projects table and returns it.
        """

        if table_id is None:
            # If id not specified, use id of the latest migration table created.
            table_id = self.cursor.execute('SELECT id FROM migrations ORDER BY id DESC LIMIT 1;').fetchone()[0]

        table_name = f'projects_{table_id}'

        self.cursor.execute(f'SELECT * FROM {table_name};')
        rows = self.cursor.fetchall()
        projects = {}
        for row in rows:
            id, name, path, link, last_modified, size = row
            projects[name] = {'path': path, 'link': link, 'last_modified': last_modified, 'size': size}
        return projects


    def write_chat_history(self, chat_history):
        """
        Writes chat history data to the chat_history table.
        If user is logged in, uploads chat history to the Replit Migrator Database Server.
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

        # Check if user is logged in.
        if self.check_if_logged_in():
            # User is logged in. Get login details.
            login_details = self.read_login_details()
            # Upload chat history to the Replit Migrator Database Server.
            self.upload_database_to_server(login_details['username'], login_details['password'])
    

    def read_chat_history(self):
        """
        Reads chat history data from the chat_history table.
        """

        self.cursor.execute('SELECT * FROM chat_history;')
        rows = self.cursor.fetchall()
        chat_history = []
        for row in rows:
            id, role, content = row
            chat_history.append({'role': role, 'content': content})
        return chat_history


    def write_login_details(self, username, password):
        """
        Writes login details to the login_details table.
        """

        # Delete any previous details.
        self.cursor.execute('DELETE FROM login_details')

        # Insert login details into database.
        self.cursor.execute('''
            INSERT INTO login_details (username, password)
            VALUES (?, ?);
        ''', (username, password))
        self.conn.commit()
    

    def delete_login_details(self):
        """
        Deletes login details from the login_details table.
        """

        # Delete all rows from the login_details table.
        self.cursor.execute('DELETE FROM login_details')
        self.conn.commit()

    
    def read_login_details(self):
        """
        Reads login details from the login_details table.
        """

        # Get login details from the login_details table.
        self.cursor.execute('SELECT * FROM login_details;')
        rows = self.cursor.fetchall()

        # Check if login details exist.
        if len(rows) == 0:
            # No login details found. Return None.
            return None
        
        # Login details found. Return them.
        login_details = {
            'username': rows[0][1],
            'password': rows[0][2]
        }
        return login_details


    def check_if_logged_in(self):
        """
        Checks if the user is logged in.
        """

        # Read login details from the login_details table.
        login_details = self.read_login_details()

        # Check if login details exist.
        if login_details is None:
            # Login details not found.
            return False
        
        # Login details found.
        return True


    def convert_database_to_dict(self):
        """
        Collect all the data in the SQLite3 database into a dictionary and return it.
        """

        # Create dictionary to store data.
        data = {
            'migrations': [],
            'chat_history': []
        }

        # Get migrations data.
        migrations = self.get_migration_tables()

        # Add projects data to migrations and add to data.
        for migration in migrations:
            migration['projects'] = self.read_projects(migration['id'])
            data['migrations'].append(migration)
        
        # Get chat history data.
        chat_history = self.read_chat_history()

        # Add chat history data to data.
        data['chat_history'] = chat_history

        return data
        

    def load_database_from_dict(self, data):
        """
        Accepts a dictionary containing data and loads it into the SQLite3 database.
        """

        # Check if data is empty. If so, exit function.
        if len(data) == 0:
            return

        # Get list of all tables in existing database.
        self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")

        # Delete all tables in existing database.
        for table in self.cursor.fetchall():
            self.cursor.execute(f'DROP TABLE {table[0]};')

        # Create new tables.
        self.create_tables()

        # Add migrations data to database.
        for migration in data['migrations']:
            self.create_migration_table(migration['date_time'])
            self.write_projects(migration['projects'], migration['id'])

        # Add chat history data to database.
        self.write_chat_history(data['chat_history'])

        # Commit changes to database.
        self.conn.commit()


    def upload_database_to_server(self, username, password):
        """
        Uploads the database for the given user to the Replit Migrator Database Server.
        """

        # Convert SQLite3 database to dictionary.
        user_data = self.convert_database_to_dict()

        # Upload existing migration data and chat history to Replit Migrator Database.
        response = requests.post(f'{self.API_ROOT_URL}api/', data={'username': username, 'password': password, 'json': json.dumps(user_data)})

        return response


    def download_database_from_server(self, username, password):
        """
        Downloads the database for the given user from the Replit Migrator Database Server.
        """

        # Attempt to retrieve user migration data from the API.
        response = requests.get(f'{self.API_ROOT_URL}api/', params={'username': username, 'password': password})

        # Parse and store JSON data in variable.
        response_json = json.loads(response.text)

        # Check for error.
        if 'status' in response_json and response_json['status'] == 'error':
            # Server responded with an error. Notify user of error and exit.
            return response
        
        # Send JSON data to database handler for parsing and storage.
        self.load_database_from_dict(response_json)

        return response

