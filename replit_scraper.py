import time
import os
import tkinter as tk
from tkinter import messagebox
from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from urllib.parse import urlparse, urlunparse

class ReplitScraper:
    def __init__(self, root):
        self.root = root

        self.create_gui()

        # Set default values from environment variables
        default_username = os.getenv('REPLIT_USERNAME')
        default_email = os.getenv('REPLIT_EMAIL')
        default_password = os.getenv('REPLIT_PASSWORD')

        # If environment variables are not set, use empty strings as defaults
        default_username = default_username if default_username else ''
        default_email = default_email if default_email else ''
        default_password = default_password if default_password else ''

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
        downloaded_folders = set()
        base_url = 'https://replit.com/@'   # base url used for accessing Replit.
        self.download_replits_recursive(driver, username, f'{base_url}{username}', downloaded_folders)
        driver.quit()

        # Download is complete. Notify user and clean up resources.
        messagebox.showinfo('Download Complete', 'Repl.its downloaded successfully.')


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

        # Delay for login form to complete and submit.
        time.sleep(2)


    def setup_webdriver(self):
        """Creates the webdriver used to access Replit."""

        # Set the download directory
        download_directory = os.path.join(os.getcwd(), 'output')

        # Setup Selenium WebDriver
        chrome_driver_path = os.path.normpath(r'C:\Users\brian\AppData\Local\chromedriver-win64\chromedriver.exe')

        # Configure ChromeOptions to set the download directory.
        chrome_options = Options()
        prefs = {'download.default_directory': download_directory}
        chrome_options.add_experimental_option('prefs', prefs)

        # Create driver.
        chrome_service = ChromeService(chrome_driver_path)
        driver = webdriver.Chrome(service=chrome_service, options=chrome_options)

        return driver


    def download_replits_recursive(self, driver, username, folder_link, downloaded_folders):
        """Recursively downloads repls inside folder and all subfolders."""

        # Exit if the folder has already been processed (avoid double downloading a folder).
        if folder_link in downloaded_folders:
            return

        # Add the current folder to the set of downloaded folders.
        downloaded_folders.add(folder_link)

        # Open the folder tab.
        new_handle = self.open_tab(driver, folder_link)

        # Switch to the newly opened tab.
        driver.switch_to.window(new_handle)

        # Download repls inside the current folder.
        self.download_repls_in_folder(driver, username)

        # Extract links to subfolders.
        subfolder_links = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}?path=folder")]')]

        # Recursively download repls inside subfolders.
        for subfolder_link in subfolder_links:
            self.download_replits_recursive(driver, username, subfolder_link, downloaded_folders)
        
        # Close original tab after all finished with.
        driver.switch_to.window(new_handle)
        driver.close()
        driver.switch_to.window(driver.window_handles[-1])


    def download_repls_in_folder(self, driver, username):
        """Downloads all replits in the folder of the currently opened tab of the driver."""

        # Extract links to repls inside the current folder
        repl_links = [a.get_attribute('href') for a in driver.find_elements(By.XPATH, f'//a[contains(@href, "/@{username}/") and not(contains(@href, "?path="))]')]

        # Download repls from all links.
        old_handles = driver.window_handles # stored to track when download tabs close.
        for link in repl_links:
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
