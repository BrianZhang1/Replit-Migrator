# Contains the ReplitScraper class which downloads all repls from a Replit user's profile.

import time
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urlunparse
import os
import shutil

class ReplitScraper:
    def __init__(self, root):
        self.root = root
        self.file_hierarchy = {} # Stores the file hierarchy of the repls.

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

        # Create label and entry for username, email, and password.
        username_label = tk.Label(self.root, text='Replit Username:')
        username_var = tk.StringVar()
        self.username_entry = tk.Entry(self.root, textvariable=username_var)
        email_label = tk.Label(self.root, text='Email:')
        email_var = tk.StringVar()
        self.email_entry = tk.Entry(self.root, textvariable=email_var)
        password_label = tk.Label(self.root, text='Password:')
        password_var = tk.StringVar()
        self.password_entry = tk.Entry(self.root, textvariable=password_var, show='*')

        download_button = tk.Button(self.root, text='Download Repl.its', command=self.begin_downloading_replits)

        # Grid layout widgets
        username_label.grid(row=0, column=0, padx=10, pady=5, sticky='e')
        self.username_entry.grid(row=0, column=1, padx=10, pady=5, sticky='w')
        email_label.grid(row=1, column=0, padx=10, pady=5, sticky='e')
        self.email_entry.grid(row=1, column=1, padx=10, pady=5, sticky='w')
        password_label.grid(row=2, column=0, padx=10, pady=5, sticky='e')
        self.password_entry.grid(row=2, column=1, padx=10, pady=5, sticky='w')
        download_button.grid(row=3, columnspan=2, pady=10)


    def begin_downloading_replits(self):
        """Initiates replit downloading process."""

        # Get input field values.
        username = self.username_entry.get()
        email = self.email_entry.get()
        password = self.password_entry.get()

        # Validate input.
        if not username or not email or not password:
            messagebox.showwarning('Warning', 'Please enter Replit username, email, and password.')
            return

        # Create webdriver.
        driver = self.setup_webdriver()

        # Login to replit.
        self.login_replit(driver, email, password)

        # Start the recursive replit downloading process.
        downloaded_folders = set()      # Stores the names of folders that have already been downloaded.
        self.download_replits_recursive(driver, username, f'https://replit.com/@{username}', downloaded_folders)

        # Scanning is complete. Notify user and clean up resources.
        self.root.attributes('-topmost', True)  # Bring the messagebox to the front
        messagebox.showinfo('Scan Complete', 'The scan is complete, however, the downloads may still be in progress. Please ensure the downloads are finished before clicking OK.')
        self.root.attributes('-topmost', False)
        driver.quit()

        # Organize files into folders based on file hierarchy.
        self.organize_files(os.path.join(os.getcwd(), 'output'))



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
        self.root.attributes('-topmost', True)  # Bring the messagebox to the front
        messagebox.showinfo('Complete CAPTCHA if applicable', 'If a CAPTCHA appeared, please complete it, click Login, and then click OK. If no CAPTCHA appeared, simply click OK.')
        self.root.attributes('-topmost', False)


    def setup_webdriver(self):
        """Creates the webdriver used to access Replit."""

        # Set the download directory
        download_directory = os.path.join(os.getcwd(), 'output')

        # Setup Selenium WebDriver
        chrome_driver_path = os.environ.get('CHROMEDRIVER_PATH')

        # Configure ChromeOptions to set the download directory.
        chrome_options = Options()
        prefs = {'download.default_directory': download_directory}
        chrome_options.add_experimental_option('prefs', prefs)
        chrome_options.add_argument('--no-sandbox')

        # Create driver.
        chrome_service = ChromeService(chrome_driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        return driver


    def download_replits_recursive(self, driver, username, folder_link, downloaded_folders, path=''):
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
        self.download_repls_in_folder(driver, username, path)

        # Extract links to subfolders.
        subfolder_links = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}?path=folder")]')]

        # Recursively download repls inside subfolders.
        for subfolder_link in subfolder_links:
            new_path = path+f'{subfolder_link.split("/")[-1]}/'
            self.download_replits_recursive(driver, username, subfolder_link, downloaded_folders, new_path)
        
        # Close original tab after all finished with.
        driver.switch_to.window(new_handle)
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])  # Switch to the last tab, or else the driver will be stuck on the closed tab.


    def download_repls_in_folder(self, driver, username, path):
        """Downloads all replits in the folder of the currently opened tab of the driver."""

        # Extract links to repls inside the current folder
        repl_links = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}/") and not(contains(@href, "?path="))]')]

        # Download repls from all links.
        old_handles = driver.window_handles # stored to track when download tabs close.
        for link in repl_links:
            file_name = link.split("/")[-1]
            self.file_hierarchy[file_name] = path
            download_url = f'{self.remove_query_params(link)}.zip'
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
        """Organizes the downloaded files into folders based on the file hierarchy."""

        for file_name, file_location in self.file_hierarchy.items():
            # Create the destination folder if it doesn't exist
            destination_folder = os.path.join(output_folder, file_location)
            os.makedirs(destination_folder, exist_ok=True)

            # Move the file to the destination folder
            source_file = os.path.join(output_folder, f"{file_name}.zip")
            destination_file = os.path.join(destination_folder, f"{file_name}.zip")
            shutil.move(source_file, destination_file)
