# Contains the ReplitScraper class which downloads all repls from a Replit user's profile.

import time
import tkinter as tk
from tkinter import ttk
from tkinter import scrolledtext
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urlunparse
import os
import zipfile
import shutil
import threading

class ScraperScreen:
    def __init__(self, root, data_handler):
        self.root = root
        self.data_handler = data_handler
        self.projects = {} # Stores project data (name, path, link).
        self.output_path = os.path.join(os.getcwd(), 'output/')

        # List of configuration files/directories/file extensions to ignore during scraping.
        # Populated by self.read_ignore_file() which is called when scraping begins.
        self.replit_ignore_dirs = []
        self.replit_ignore_files = []
        self.replit_ignore_extensions = []

        self.create_gui()

        # Set default values from environment variables
        default_username = os.getenv('REPLIT_USERNAME')
        default_email = os.getenv('REPLIT_EMAIL')
        default_password = os.getenv('REPLIT_PASSWORD')

        # If environment variables are not set, use empty strings as defaults
        default_username = default_username if default_username else ''
        default_email = default_email if default_email else ''
        default_password = default_password if default_password else ''

        # Set default values in the GUI entries.
        self.username_entry.insert(0, default_username)
        self.email_entry.insert(0, default_email)
        self.password_entry.insert(0, default_password)


    def create_gui(self):
        """Creates Tkinter GUI."""

        # Create frame that wraps this screen.
        self.frame = tk.Frame(self.root)

        # Create label and entry for username, email, and password.
        username_label = tk.Label(self.frame, text='Replit Username:')
        username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.frame, textvariable=username_var)
        email_label = tk.Label(self.frame, text='Email:')
        email_var = tk.StringVar()
        self.email_entry = tk.Entry(self.frame, textvariable=email_var)
        password_label = tk.Label(self.frame, text='Password:')
        password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.frame, textvariable=password_var, show='*')

        # Create download button to initiate migration.
        download_button = tk.Button(self.frame, text='Download Repl.its', command=self.begin_downloading_repls)

        # Create status scrolledtext.
        self.status_label = tk.Label(self.frame, text='Migration Status')
        self.status_scrolledtext = scrolledtext.ScrolledText(self.frame, height=10, width=80)
        self.status_scrolledtext.insert(tk.END, 'Status updates will appear here once migration has begun.\n')
        self.status_checkbox = ttk.Checkbutton(self.frame, text='Show status updates', command=self.toggle_status_updates, state='selected')
        self.status_checkbox.state(['selected'])

        # Grid layout widgets.
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        email_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.email_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        password_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        download_button.grid(row=3, columnspan=2, pady=10)
        self.status_label.grid(row=4, columnspan=2, pady=(10, 0))
        self.status_checkbox.grid(row=5, columnspan=2)
        self.status_scrolledtext.grid(row=6, columnspan=2, padx=10, pady=5)


    def begin_downloading_repls(self):
        """Initiates repl downloading process."""

        # Update status to indicate download has begun.
        self.status_scrolledtext.insert(tk.END, 'Repl migration initiated.\n')

        # Read files to ignore from replit_ignore.txt
        self.read_ignore_file()

        # Get input field values.
        self.status_scrolledtext.insert(tk.END, 'Retrieving login credentials from input fields...\n')
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Validate input.
        if not username or not email or not password:
            messagebox.showwarning('Warning', 'Please enter Replit username, email, and password.')
            return

        # Create output folder (where files are downloaded to).
        self.status_scrolledtext.insert(tk.END, 'Creating output directory...\n')
        os.makedirs(self.output_path, exist_ok=True)

        # Execute webdriver in a separate thread to prevent GUI from freezing.
        self.status_scrolledtext.insert(tk.END, 'Creating thread to execute browser emulator...\n')
        thread = threading.Thread(target=self.execute_webdriver_thread, args=(username, email, password))
        self.scraping_finished = False
        thread.start()

        # Continuously check whether thread operation has finished, proceed when scraping is complete.
        while not self.scraping_finished:
            # Update GUI to prevent freezing.
            self.root.update()
            # Automatically scroll to the bottom of the status scrolledtext.
            self.status_scrolledtext.see(tk.END)

        # Organize files into folders based on file hierarchy.
        self.status_scrolledtext.insert(tk.END, 'Organizing files...\n')
        self.status_scrolledtext.see(tk.END)
        self.organize_files(self.output_path)

        # Write data to database.
        self.status_scrolledtext.insert(tk.END, 'Updating database...\n')
        self.status_scrolledtext.see(tk.END)
        self.data_handler.create_migration_table(time.strftime('%Y-%m-%d %H:%M:%S'))
        self.data_handler.write_projects(self.projects)

        # Update status to indicate migration has completed.
        self.status_scrolledtext.insert(tk.END, 'Migration complete.\n')
        self.status_scrolledtext.see(tk.END)
        self.status_scrolledtext.configure(state='disabled')


    def read_ignore_file(self):
        """Reads files to ignore from replit_ignore.txt."""

        with open('replit_ignore.txt', 'r') as file:
            # Tracks the type of item currently being read (directories or files).
            currently_reading = None
            for line in file:
                if line.startswith('#'):
                    # Ignore comments.
                    continue
                if line.startswith('@'):
                    if line.startswith('@(DIRECTORIES)'):
                        # Begin reading directories
                        currently_reading = 'directories'
                        continue
                    if line.startswith('@(FILES)'):
                        # Begin reading files
                        currently_reading = 'files'
                        continue
                line = line.strip()
                if len(line) > 0:
                    # Add item name to appropriate list.
                    if currently_reading == 'directories':
                        self.replit_ignore_dirs.append(line)
                    elif currently_reading == 'files':
                        if line.startswith('*.'):
                            # Add file extension to list of extensions to ignore.
                            self.replit_ignore_extensions.append(line[2:])
                        else:
                            self.replit_ignore_files.append(line)


    def execute_webdriver_thread(self, username, email, password):
        """Executes the webdriver in a separate thread to prevent GUI from freezing."""

        # Create webdriver.
        self.status_scrolledtext.insert(tk.END, 'Creating browser emulator...\n')
        driver = self.setup_webdriver()

        # Login to replit.
        self.status_scrolledtext.insert(tk.END, 'Logging into Replit...\n')
        self.login_replit(driver, email, password)
        self.status_scrolledtext.insert(tk.END, 'Login successful.\n')

        # Start the recursive repl downloading process.
        self.status_scrolledtext.insert(tk.END, 'Beginning download process...\n')
        downloaded_folders = set()      # Stores the names of folders that have already been downloaded.
        self.download_repls_recursive(driver, username, f'https://replit.com/@{username}', downloaded_folders)
        self.status_scrolledtext.insert(tk.END, 'Download process complete.\n')

        # Scanning is complete. Notify user and clean up resources.
        messagebox.showinfo('Scan Complete', 'The scan is complete, however, the downloads may still be in progress. Please ensure the downloads are finished before clicking OK.')
        self.status_scrolledtext.insert(tk.END, 'Exiting browser emulator...\n')
        driver.quit()

        # Notify main thread that scraping is complete.
        self.scraping_finished = True


    def login_replit(self, driver, email, password):
        """Uses existing driver to log into replit."""

        # Navigate to login page.
        driver.get('https://replit.com/login')

        # Fill in the login form.
        email_input = driver.find_element(By.NAME, 'username')
        password_input = driver.find_element(By.NAME, 'password')
        email_input.send_keys(email)
        password_input.send_keys(password)

        # Click the Log In button.
        login_button = driver.find_element(By.CSS_SELECTOR, '[data-cy="log-in-btn"]')
        login_button.click()

        # Allow user to handle CAPTCHA if it appears.
        messagebox.showinfo('Complete CAPTCHA if applicable', 'If a CAPTCHA appeared, please complete it, click Login, and then click OK. If no CAPTCHA appeared, simply click OK.')


    def setup_webdriver(self):
        """Creates the webdriver used to access Replit."""

        # Setup Selenium WebDriver
        chrome_driver_path = os.environ.get(r'C:\Users\brian\AppData\Local\chromedriver-win64\chromedriver.exe')

        # Configure ChromeOptions to set the download directory.
        chrome_options = Options()
        prefs = {'download.default_directory': self.output_path}
        chrome_options.add_experimental_option('prefs', prefs)

        # Create driver.
        chrome_service = ChromeService(chrome_driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        return driver


    def download_repls_recursive(self, driver, username, folder_link, downloaded_folders, path=''):
        """
        Recursively downloads repls inside folder and all subfolders.
        
        Args:
            driver: Selenium webdriver.
            username: Replit username.
            folder_link: Link to the folder currently being processed.
            downloaded_folders: Set of folders that have already been downloaded.
            path: Path to the current folder in Replit file hierarchy.
        """

        # Exit if the folder has already been processed (avoid double downloading a folder).
        if folder_link in downloaded_folders:
            return

        # Add the current folder to the set of downloaded folders.
        downloaded_folders.add(folder_link)

        # Open the folder tab.
        new_handle = self.open_tab(driver, folder_link)

        # Switch to the newly opened tab.
        driver.switch_to.window(new_handle)
        time.sleep(3)   # Wait for the page to load.

        # Download repls inside the current folder.
        self.status_scrolledtext.insert(tk.END, 'Currently downloading folder: '+path+'\n')
        self.download_repls_in_folder(driver, username, path)

        # Extract links to subfolders.
        self.status_scrolledtext.insert(tk.END, 'Extracting subfolders...\n')
        subfolder_links = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}?path=folder")]')]

        # Recursively download repls inside subfolders.
        for subfolder_link in subfolder_links:
            new_path = path+f'{subfolder_link.split("/")[-1]}/'
            self.download_repls_recursive(driver, username, subfolder_link, downloaded_folders, new_path)
        
        # Close original tab after all finished with.
        driver.switch_to.window(new_handle)
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab, or else the driver will be stuck on the closed tab.


    def download_repls_in_folder(self, driver, username, path):
        """Downloads all repls in the folder of the currently opened tab of the driver."""

        # Extract links to repls inside the current folder
        anchor_attributes = driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}/") and not(contains(@href, "?path="))]')
        repl_links = [a.get_attribute('href') for a in anchor_attributes]
        last_modified = [a.find_elements(By.XPATH, './div[1]/div[2]/div[1]/span[1]')[0].text for a in anchor_attributes]
        size = [a.find_elements(By.XPATH, './div[1]/div[2]/div[1]/span[2]')[0].text for a in anchor_attributes]
        

        # Download repls from all links.
        old_handles = driver.window_handles # stored to track when download tabs close.
        n_repls = len(repl_links)
        for i, link in enumerate(repl_links):
            file_name = link.split("/")[-1]
            self.projects[file_name] = {
                'path': path, 
                'link': link, 
                'last_modified': last_modified[i], 
                'size': size[i]
                }
            download_url = f'{self.remove_query_params(link)}.zip'
            self.status_scrolledtext.insert(tk.END, f'\t({i+1}/{n_repls}) Downloading project "{file_name}"...\n')
            driver.execute_script(f'window.open("{download_url}", "_blank");')

        # Wait for download tabs to close.
        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            if len(driver.window_handles) == len(old_handles):
                return

        raise TimeoutError('Timed out waiting for download tabs to close.')


    def remove_query_params(self, url):
        """Remove query parameters from a URL."""
        parts = urlparse(url)
        return urlunparse(parts._replace(query=''))


    def open_tab(self, driver, link):
        """Opens a tab, waits for it to open, and returns its handle."""

        # Store old handles (compared to new handles).
        old_handles = driver.window_handles

        # Open a new tab to navigate to the folder
        driver.execute_script(f'window.open("{link}", "_blank");')

        # Wait for tab to open and return its handle.
        timeout = 10
        start_time = time.time()
        while time.time() - start_time < timeout:
            new_handles = [handle for handle in driver.window_handles if handle not in old_handles]
            if new_handles:
                return new_handles[0]

        raise TimeoutError('Timed out waiting for the new tab to open.')


    def organize_files(self, output_folder):
        """Unzips and organizes the downloaded files into folders based on the file hierarchy."""

        for project_name, project_data in self.projects.items():
            # Determine absolute paths of source file and destination folder.
            project_location = project_data['path']
            source_file = os.path.join(output_folder, f"{project_name}.zip")
            destination_folder = os.path.join(output_folder, project_location, project_name)

            # Update GUI and automatically scroll to prevent freezing during unzipping process.
            self.status_scrolledtext.insert(tk.END, f'Unzipping {project_name}...\n')
            self.root.update()
            self.status_scrolledtext.see(tk.END)

            self.unzip_and_delete(source_file, destination_folder)

        # Deletes all configuration files automatically generated by Replit.
        self.status_scrolledtext.insert(tk.END, 'Deleting ignored files and directories...\n')
        self.status_scrolledtext.see(tk.END)
        self.delete_ignored_files()


    def unzip_and_delete(self, zip_file_path, extract_to_path):
        """Unzips target zip file to designated path. Deletes zip file once complete."""

        try:
            # Open the zip file.
            with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                # Extract all the contents to the specified path.
                zip_ref.extractall(extract_to_path)
                
            # Remove the zip file after extraction.
            os.remove(zip_file_path)
            
        except Exception as e:
            # Print any exceptions that occur.
            print(f"Error: {e}")


    def delete_ignored_files(self):
        """Deletes files and directories listed in replit_ignore.txt"""

        for root, dirs, files in os.walk('output/'):
            # Remove ignored files.
            for file in files:
                # Check if extension is ignored.
                extension = file.split('.')[-1]
                if extension in self.replit_ignore_extensions:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)
                # Check if file name is ignored.
                if file in self.replit_ignore_files:
                    file_path = os.path.join(root, file)
                    os.remove(file_path)

            # Remove ignored directories.
            for dir in dirs:
                if dir in self.replit_ignore_dirs:
                    dir_path = os.path.join(root, dir)
                    shutil.rmtree(dir_path)


    def toggle_status_updates(self):
        """Toggles visibility of the status updates scrolledtext"""

        if self.status_checkbox.instate(['selected']):
            self.status_scrolledtext.grid()
        else:
            self.status_scrolledtext.grid_remove()





        

        


        
