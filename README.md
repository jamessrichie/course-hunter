# course-hunter

Course-Hunter automates your browser to register for courses as soon as a trigger event occurs. This trigger
event could be a text message, an email, or a specified time, depending on the listener function used.
* Course-Hunter is designed to work with macOS and Safari, but should require minimal modifications to work
  with other operating systems and browsers.


## Disclaimer
* The use of automated tools such as this one is expressly forbidden by UW, and as such, this program exists
  purely as a proof of concept and a personal exploration into Web automation.
* The developers strictly discourage the use and distribution of Course-Hunter for actual registration purposes.
* The developers are not responsible for any issues that arise from its use, including software bugs, registration
  mistakes, and sanctions from UW.



## Getting started

### Prerequisites

Course-Hunter requires [Python 3](https://www.python.org/downloads/) to run. Development and testing was done
in Python 3.9 (x86 version).

#### Email Listener

Course-Hunter's email listener requires a Gmail account. This can be a dummy account and does not have to be monitored.

#### Text Message Listener

Course-Hunter's text message listener requires an iPhone, a MacBook, and an iCloud account with enough storage to sync
iMessages.


### Installation

1. Clone the Git repository.
2. Navigate to the Course-Hunter root directory and run `setup.sh`.

        terminal% sh setup.sh

3. Grant all requested permissions.

This should automatically configure Safari and grant Course-Hunter the necessary system permissions. If something
goes wrong, continue reading for manual setup instructions.

#### Manually Setting up Safari

1. Open Safari and in the menu bar, choose 'Safari' > 'Settings…', click 'Advanced', then select
   'Show Develop menu in menu bar.'
2. Select the 'Develop' menu within the Safari menu bar.
3. Make sure that 'Allow Remote Automation' is selected.

#### Manually Setting up System Permissions

1. Go to 'System Settings' > 'Privacy & Security.'
2. Make sure 'Full Disk Access' > 'Terminal' is selected.
3. Make sure 'Automation' > 'Terminal' > 'System Events' is selected.

#### Manually Setting up Python 3

Course-Hunter requires the following Python packages to run.

```
terminal% pip3 install DateTime
terminal% pip3 install selenium
terminal% pip3 install imessage-reader
```

#### Manually Configuring Git

This safeguard against pushing your credentials and configurations files to Git.

```
git update-index --skip-worktree config/credentials.json
git update-index --skip-worktree config/joint-registration.json
```


### Configuration

The 'config' folder stores all the configuration files for Course-Hunter.

#### Configuring `credentials.json`

This file stores your UW NetID credentials. If you choose to enable the email listener, this file also stores your
Gmail account credentials. Note that the field `gmail_app_password` is _not_ your Gmail account password. We will
discuss how to generate a Gmail app password under ['Setting up Your Course-Hunter Email.'](#setup-email)

#### Configuring `joint-registration.json`

We may need to register for a lecture and a lab section together, or add and drop courses simultaneously. This file
stores which courses need to be jointly added and dropped. Refer to the following examples to understand the expected
structure of this file.

<details>
  <summary><h4 style="display: inline">Example 1: Jointly adding courses</h4></summary>

    {
      "data": [
        {
          "add": ["10000", "11000"],
          "drop": []
        }
      ]
    }

When Course-Hunter detects that _either_ course is available, it will register for _both_ courses.
</details>

<details>
  <summary><h4 style="display: inline">Example 2: Jointly adding and dropping courses</h4></summary>

    {
      "data": [
        {
          "add": ["10000"],
          "drop": ["11000"]
        }
      ]
    }

When Course-Hunter detects that SLN: 10000 is available, it will add SLN: 10000 and drop SLN: 11000
simultaneously. If Course-Hunter fails to register for SLN: 10000, then it will not drop SLN: 11000.
</details>

<details>
  <summary><h4 style="display: inline">Example 3: Jointly adding and dropping multiple groups of courses</h4></summary>

    {
      "data": [
        {
          "add": ["10000", "11000"],
          "drop": ["12000"]
        },
        {
          "add": ["20000"],
          "drop": ["21000", "22000"]
        }
      ]
    }

When Course-Hunter detects that either SLN: 10000 or 11000 is available, it will add SLNs: 10000 and
11000 and drop SLN: 12000 simultaneously. It will _not_ add or drop anything from the other group.
</details>

##### Noteworthy Edge Cases

* You are allowed to specify the same add SLN code in multiple groups. When Course-Hunter detects that this course is
  available, it will only consider the first group that contains this add SLN code.
* If you specify a drop SLN code for a class you are not registered for, Course-Hunter will ignore the drop SLN code and
  proceed as usual.

### <span id="setup-email">Setting up Your Email for the Email Listener</span>

Course-Hunter's email listener will trigger when you receive a Notify.UW email. We will need to allow Course-Hunter to
connect to your email.

1. Visit [Gmail](https://mail.google.com/) and log into your Gmail account.
2. Press the gear icon in the top-right corner and select 'See All Settings.'
3. Go to the 'Forwarding and POP/IMAP' tab and select 'Enable IMAP'. Make sure to save your changes.
4. Press the profile icon in the top-right corner and select 'Manage Your Google Account.'
5. Go to the 'Security' tab and activate '2-Step Verification.'
6. Once set up, return to the 'Security' tab and select 'App Passwords.'
7. Select 'Mail' as your app and 'Mac' as your device and generate the app password.
8. Store this app password in the field `gmail_app_password` in `credentials.json`.

To start the email listener, create an `EmailListener` object and call `start()`.


### Setting up iMessage for the Text Message Listener

Course-Hunter's text message listener will trigger when you receive a Notify.UW text. In order to access your
phone's text messages from a computer, we will make use of iCloud's iMessage syncing feature.

1. Make sure you are logged into the same iCloud account on your iPhone and MacBook.
2. On your iPhone, make sure 'Settings' > [Your Name] > 'iCloud' > 'Show All' > 'Messages' > 'Sync this iPhone'
   is selected.
3. On your MacBook, open 'Messages' and in the menu bar, choose 'Messages' > 'Settings…', click 'iMessage', then select
   'Enable Messages in iCloud.'

To start the text message listener, create an `iMessageListener` object and call `start()`.


### Setting up the Time Listener

Course-Hunter's time listener will trigger at a specified time, adding and dropping courses from the first group in
`joint-registration.json`.

To start the time listener, create a `TimeListener` object and call `start()`.
* You are allowed to create multiple `TimeListener` instances to trigger at various times

<details>
  <summary><h4 style="display: inline">Example</h4></summary>

    {
      "data": [
        {
          "add": ["10000", "11000"],
          "drop": []
        },
        {
          "add": ["20000", "21000"],
          "drop": ["22000"]
        }
      ]
    }

At the specified time, Course-Hunter will register for SLNs: 10000 and 11000. It will _not_ add or drop anything
from the other group.
</details>



## Running the Program

You're all set! Navigate to the Course-Hunter root directory and run `main.py` to start the program.

    terminal% python main.py

On your first run, Course-Hunter will log into your UW NetID account and you will be asked to verify the login on your
2FA device. On subsequent runs, Course-Hunter will automatically bypass 2FA and start running immediately. You will
only be asked to log into your UW NetID account again if your 2FA cookies expire, or if you made changes to
`credentials.json`.
* Course-Hunter will preemptively refresh 2FA cookies if they are expiring in the next 5 days. If you intend to leave
  Course-Hunter running for longer than that, you should force a refresh by deleting `hash.txt`.
* It is recommended that you disable 'Turn display off when inactive' on your computer.