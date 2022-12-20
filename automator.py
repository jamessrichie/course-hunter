import json
import time
import hashlib
import selenium
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class Automator:

    # URL of test page
    TEST_URL = "https://my.uw.edu"

    # URL of registration page
    TARGET_URL = "https://sdb.admin.uw.edu/students/uwnetid/register.asp"

    # URL of login page
    WAIT_URL = "https://idp.u.washington.edu"

    # URL loading timeout
    TIMEOUT = 10

    # URL loading timeout for possibly slow services. You may want to increase this
    # to up to 150 when expecting slow services such as during registration periods
    TIMEOUT_LONG = 60

    # Initialize object and verify NetID credentials
    def __init__(self, JOINT_SLN_CODES_LIST):
        self.JOINT_SLN_CODES_LIST = JOINT_SLN_CODES_LIST

        # Load JSON file containing credentials and generate cookies
        try:
            credentials_file = open("credentials.json", "r")
            credentials = json.load(credentials_file)

            # Web cookie asserting 2FA 'Remember Me' is enabled for this web client
            self.uw_optin = {
                "name": "uw-optin-" + credentials["uw_netid"],
                "value": "yes"
            }

            # Web cookie verifying 2FA 'Remember Me' is enabled for this web client
            self.uw_remember_me = {
                "name": "uw-rememberme-" + credentials["uw_netid"],
                "value": credentials["uw_remember_me_cookie"]
            }

            # Set the form field names and values
            self.form_fields = {
                "weblogin_netid": credentials["uw_netid"],
                "weblogin_password": credentials["uw_netid_password"]
            }
            self.verify_setup(credentials_file)
            credentials_file.close()

        except FileNotFoundError:
            print("Could not find credentials.json. Check that the file exists in the root directory")
            exit()

        except KeyError:
            print("credentials.json is missing one or more important key-values")
            exit()

    # Verifies that UW credentials are valid
    def verify_setup(self, credentials_file):
        f = open("hash.txt", "r+")
        stored_credentials_hash = f.readline()
        credentials_hash = str(hashlib.md5(credentials_file.read().encode("utf-8")).hexdigest())

        # Check if credentials match those already verified
        if stored_credentials_hash == credentials_hash:
            print("Automator: Initialized")
            return

        # Open the Safari browser
        browser = webdriver.Safari()
        browser.set_window_size(1300, 800)

        # Go to MyUW
        browser.get(self.TEST_URL)

        # Login to MyUW
        self.login(browser)

        # Wait for redirect to MyUW
        try:
            element_present = EC.presence_of_element_located((By.CLASS_NAME, 'myuw-body'))
            WebDriverWait(browser, self.TIMEOUT).until(element_present)
            print("Automator: Initialized")

        except TimeoutException:
            print("Automator: Incorrect setup. Check your UW Net ID credentials and 2FA cookies")
            exit()

        # Close browser once finished
        browser.close()

        # Record that credentials have been verified
        f.write(credentials_hash)
        f.close()

    # Registers the supplied SLN code
    def register(self, sln_code):
        joint_add_sln_codes, joint_drop_sln_codes = self.get_joint_sln_codes(sln_code)

        try:
            # Open the Safari browser
            browser = webdriver.Safari()
            browser.set_window_size(1300, 800)

        except selenium.common.exceptions.SessionNotCreatedException:
            raise Exception(sln_code)

        # Go to the registration page
        browser.get(self.TARGET_URL)

        # If login failed or could not reach registration page, then exit
        if not self.login(browser) or not self.wait_for_registration_page(browser):
            print("Automator: Failed to send SLN(s): {} to registration".format(",".join(joint_add_sln_codes)))
            return

        # Populate the add SLN forms
        sln_index = 0
        table_index = 1
        drop_indexes = []
        while sln_index < len(joint_add_sln_codes):
            input_field = browser.find_element(By.NAME, f"sln{table_index}")
            input_field_value = input_field.get_attribute('value')

            if input_field_value == "":
                input_field.send_keys(joint_add_sln_codes[sln_index])
                sln_index += 1
            elif input_field_value in joint_drop_sln_codes:
                drop_indexes.append(table_index)

            table_index += 1

        # Click the drop SLN checkboxes
        for drop_index in drop_indexes:
            check_box = browser.find_element(By.NAME, f"action{drop_index}")
            check_box.click()

        # Clicks the submit button
        browser.find_elements(By.TAG_NAME, "input")[-1].click()

        # Allow delay for registration page to refresh
        time.sleep(1)

        if not self.wait_for_registration_page(browser):
            print("Automator: Sent SLN(s): {} to registration, ".format(",".join(joint_add_sln_codes)) +
                  "but timed out before being able to confirm your registration status")

        elif "Schedule not updated." in browser.page_source:
            print("Automator: Sent SLN(s): {} to registration, but did not get the spot(s)"
                  .format(",".join(joint_add_sln_codes)))

        elif "Schedule updated." in browser.page_source:
            print("Automator: Successfully registered for SLN(s): {} and dropped SLN(s): {}"
                  .format(",".join(joint_add_sln_codes), ",".join(joint_drop_sln_codes)))

        else:
            print(joint_add_sln_codes)
            print("Automator: Sent SLN(s): {} to registration, ".format(",".join(joint_add_sln_codes)) +
                  "but could not interpret the displayed registration status")

    # Returns all SLN codes that must be added and dropped jointly with the supplied SLN code
    def get_joint_sln_codes(self, sln_code):
        for joint_sln_codes in self.JOINT_SLN_CODES_LIST:

            joint_add_sln_codes = joint_sln_codes[0]
            joint_drop_sln_codes = joint_sln_codes[1]

            if sln_code in joint_add_sln_codes:
                return joint_add_sln_codes, joint_drop_sln_codes
        return [sln_code], []

    # Wait for login page to load
    def wait_for_login_page(self, browser):
        try:
            element_present = EC.presence_of_element_located((By.ID, 'uwsignin'))
            WebDriverWait(browser, self.TIMEOUT).until(element_present)
            return True

        except TimeoutException:
            print("Automator: Timed out waiting for login page to load")
            return False

    # Wait for registration page to load
    def wait_for_registration_page(self, browser):
        try:
            element_visible = EC.visibility_of_element_located((By.ID, 'doneDiv'))
            WebDriverWait(browser, self.TIMEOUT_LONG).until(element_visible)
            return True

        except TimeoutException:
            print("Automator: Timed out waiting for registration page to load")
            return False

    # Logs into the configured UW NetID account
    def login(self, browser):

        if not self.wait_for_login_page(browser):
            return False

        # Load 2FA bypass cookies
        browser.add_cookie(self.uw_optin)
        browser.add_cookie(self.uw_remember_me)

        # Fill out login forms
        for field in self.form_fields:
            browser.find_element(By.ID, field).send_keys(self.form_fields[field])

        # Click login button
        browser.find_element(By.ID, "submit_button").click()

        return True
