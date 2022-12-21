import json
import time
import hashlib
import selenium
from datetime import datetime, timedelta

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# URL of MyUW page
MYUW_URL = "https://my.uw.edu"

# URL of registration page
REGISTRATION_URL = "https://sdb.admin.uw.edu/students/uwnetid/register.asp"

# URL loading timeout
TIMEOUT = 10

# URL loading timeout for possibly slow services. You may want to increase this
# to up to 150 when expecting slow services such as during registration periods
TIMEOUT_LONG = 60

# Timeout before Duo 2FA login session expires
TIMEOUT_2FA = 60

# If credentials are expiring within this grace period, we will preemptively generate new ones
EXPIRATION_GRACE_PERIOD = 5


# Converts credentials.json into a dict
def extract_credentials():
    credentials_file = open("credentials.json", "r")
    credentials = json.load(credentials_file)
    credentials_file.close()

    return credentials


# Generates the hash for contents of credentials.json
def extract_credentials_hash():
    credentials = extract_credentials()
    return hashlib.md5(json.dumps(credentials).encode()).hexdigest()


# Checks that credentials.json has not been altered
def check_credentials_integrity():
    credentials_hash = extract_credentials_hash()

    try:
        hash_file = open("hash.txt", "r")
        stored_hash = hash_file.readline()
        hash_file.close()

        return credentials_hash == stored_hash

    except FileNotFoundError:
        hash_file = open("hash.txt", "w")
        hash_file.close()
        return False


# Checks that credentials are still valid
def check_credentials_expiration():
    credentials_file = extract_credentials()
    expiration_timestamp = datetime.fromtimestamp(credentials_file["expiration"])

    if expiration_timestamp > datetime.now() + timedelta(days=EXPIRATION_GRACE_PERIOD):
        return expiration_timestamp
    else:
        return None


# Creates/updates a key-value pair in credentials.json
def update_credentials(key, value):
    credentials = extract_credentials()
    credentials[key] = value

    credentials_file = open("credentials.json", "w")
    json.dump(credentials, credentials_file, indent=2, sort_keys=True)
    credentials_file.close()


# Updates the stored hash in hash.txt
def update_stored_hash():
    credentials_hash = extract_credentials_hash()

    hash_file = open("hash.txt", "w")
    hash_file.write(credentials_hash)
    hash_file.close()


# Builds cookies from credentials.json
def generate_cookies():
    credentials = extract_credentials()

    # Set the form field names and values
    form_fields = {
        "weblogin_netid": credentials["uw_netid"],
        "weblogin_password": credentials["uw_netid_password"]
    }

    # Web cookie asserting 2FA 'Remember Me' is enabled for this web client
    uw_optin = {
        "name": "uw-optin-" + credentials["uw_netid"],
        "value": "yes"
    }

    # Web cookie verifying 2FA 'Remember Me' is enabled for this web client
    uw_remember_me = {
        "name": "uw-rememberme-" + credentials["uw_netid"],
        "value": credentials["uw_remember_me_cookie"]
    }

    return form_fields, uw_optin, uw_remember_me


# Wait for MyUW page to load
def wait_for_myuw_page(browser):
    try:
        element_present = EC.presence_of_element_located((By.CLASS_NAME, 'myuw-body'))
        WebDriverWait(browser, TIMEOUT_2FA).until(element_present)
        return True

    except TimeoutException:
        print("Automator: Timed out waiting for MyUW page to load")
        return False


# Wait for login page to load
def wait_for_login_page(browser):
    try:
        element_present = EC.presence_of_element_located((By.ID, 'uwsignin'))
        WebDriverWait(browser, TIMEOUT).until(element_present)
        return True

    except TimeoutException:
        print("Automator: Timed out waiting for login page to load")
        return False


# Wait for 2FA page to load
def wait_for_2fa_page(browser):
    try:
        element_present = EC.presence_of_element_located((By.NAME, 'rememberme'))
        WebDriverWait(browser, TIMEOUT_2FA).until(element_present)
        return True

    except TimeoutException:
        print("Automator: Timed out waiting for 2FA page to load")
        return False


# Wait for registration page to load
def wait_for_registration_page(browser):
    try:
        element_visible = EC.visibility_of_element_located((By.ID, 'doneDiv'))
        WebDriverWait(browser, TIMEOUT_LONG).until(element_visible)
        return True

    except TimeoutException:
        print("Automator: Timed out waiting for registration page to load")
        return False


class Automator:

    # Initialize object and verify NetID credentials
    def __init__(self, joint_registration_list):
        self.joint_registration_list = joint_registration_list

        # Load JSON file containing credentials and generate cookies
        try:
            self.form_fields, self.uw_optin, self.uw_remember_me = generate_cookies()
            self.verify_setup()

        except FileNotFoundError as e:
            print("Could not find {}. Check that the file exists in the root directory".format(e.filename))
            exit()

        except KeyError:
            print("credentials.json is missing one or more important key-values")
            exit()

        print("Automator: Initialized")

    # Verifies that UW credentials are valid
    def verify_setup(self):
        # Verify that credentials.json has not been changed
        if check_credentials_integrity():
            print("Automator: Verified credentials.json integrity")

            # Check that stored credentials have not expired
            expiration_timestamp = check_credentials_expiration()

            if expiration_timestamp is not None:
                print("Automator: Cookies active. Will expire in {} days on {}".format((expiration_timestamp - datetime.now()).days, expiration_timestamp.date()))
                return
            else:
                print("Automator: Cookies expired. Must regenerate")
        else:
            print("Automator: credentials.json has been altered. Must re-verify credentials")

        update_credentials("uw_remember_me_cookie", "")
        self.form_fields, self.uw_optin, self.uw_remember_me = generate_cookies()

        # Open the Safari browser
        browser = webdriver.Safari()
        browser.set_window_size(1300, 800)

        # Go to MyUW
        browser.get(MYUW_URL)

        # Login to MyUW
        if not self.login_2fa(browser):
            print("Automator: Could not log into UW NetID. Check your UW NetID credentials")

        # Logout of MyUW
        browser.get(MYUW_URL + "/logout/")
        browser.get(MYUW_URL)

        # Download cookies from login page
        cookie = list(filter(lambda elt: "uw-rememberme-" in elt["name"], browser.get_cookies()))[0]

        # Update in-memory cookies
        update_credentials("uw_remember_me_cookie", cookie["value"])
        update_credentials("expiration", cookie["expiry"])
        self.form_fields, self.uw_optin, self.uw_remember_me = generate_cookies()

        # Verify cookies by logging into MyUW
        self.login(browser)

        # Wait for redirect to MyUW
        if not wait_for_myuw_page(browser):
            print("Automator: Please confirm that MyUW is not down and restart the program")
            exit()

        # Close browser once finished
        browser.close()

        # Update stored hash
        update_stored_hash()

        print("Automator: Credentials verified")

    # Registers the supplied SLN code
    def register(self, sln_code):
        joint_add_sln_codes, joint_drop_sln_codes = self.get_joint_registration(sln_code)

        try:
            # Open the Safari browser
            browser = webdriver.Safari()
            browser.set_window_size(1300, 800)

        except selenium.common.exceptions.SessionNotCreatedException:
            raise Exception(sln_code)

        # Go to the registration page
        browser.get(REGISTRATION_URL)

        # If login failed or could not reach registration page, then exit
        if not self.login(browser) or not wait_for_registration_page(browser):
            print("Automator: Failed to send SLN(s): {} to registration".format(",".join(joint_add_sln_codes)))
            return

        # Populate the SLN form
        sln_index = 0
        table_index = 1
        while sln_index < len(joint_add_sln_codes):
            input_field = browser.find_element(By.NAME, f"sln{table_index}")
            input_field_value = input_field.get_attribute('value')

            # If input field is empty, it is editable. Then add SLN code
            if input_field_value == "":
                input_field.send_keys(joint_add_sln_codes[sln_index])
                sln_index += 1

            # If input field is not empty, it stores an SLN code
            # If we want to drop this SLN code, click the associated checkbox
            elif input_field_value in joint_drop_sln_codes:
                check_box = browser.find_element(By.NAME, f"action{table_index}")
                check_box.click()

            table_index += 1

        # Clicks the submit button
        browser.find_elements(By.TAG_NAME, "input")[-1].click()

        # Allow delay for registration page to refresh
        time.sleep(1)

        # Interpret the displayed status
        if not wait_for_registration_page(browser):
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

    # Log into the configured UW NetID account
    def login(self, browser):
        if not wait_for_login_page(browser):
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

    # Log into the configured UW NetID account and handle 2FA
    def login_2fa(self, browser):
        if not self.login(browser) or not wait_for_2fa_page(browser):
            return False

        if not wait_for_myuw_page(browser):
            print("Automator: Duo 2FA login session expired. Repeating log in process")

            browser.get(MYUW_URL)
            self.login_2fa(browser)

        return True

    # Returns all SLN codes that must be added and dropped jointly with the supplied SLN code
    def get_joint_registration(self, sln_code):
        for joint_registration in self.joint_registration_list:

            joint_add_sln_codes = joint_registration["add"]
            joint_drop_sln_codes = joint_registration["drop"]

            if sln_code in joint_add_sln_codes:
                return joint_add_sln_codes, joint_drop_sln_codes

        return [sln_code], []
