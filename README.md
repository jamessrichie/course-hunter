# course-hunter

## Description

Course-Hunter listens for incoming Notify.UW emails and registers for a course as soon as
a seat opens. It may also be configured to register for courses at 6 AM on registration day
* Course-Hunter registers for a course within 15 seconds of the Notify.UW email being sent out and within
2 seconds of the Notify.UW email being received
* The use of automated tools such as this one is expressly forbidden by UW, and as such, this program exists
purely as a proof of concept and exploration into Web automation


## Getting started

### Disclaimer

These instructions are tailored for MacOS users. That said, Windows and Linux users should still be able
to follow along

### Extracting Your `uw-remember-me` Cookie

In order to circumvent UW's two-factor authentication requirement, we will need a 'Remember Me' cookie 

1. Make sure that the 'Develop' menu is enabled within the Safari menu bar. Otherwise, follow
[this](https://support.apple.com/guide/safari/use-the-developer-tools-in-the-develop-menu-sfri20948/mac)
article to enable the 'Develop' menu
2. Open a Private Browsing tab and visit [MyUW](https://my.uw.edu)
3. Once redirected to the login page, enter your UW NetID credentials and log-in
4. When asked for 2FA, select 'Remember Me on This Browser' before approving the login
5. Once redirected to the [MyUW](https://my.uw.edu) homepage, sign out of your session
6. Using the same Private Browsing tab, visit [MyUW](https://my.uw.edu) again
7. Once redirected to the login page, do not enter your UW NetID credentials
8. Right-click/secondary-click anywhere on the login page and select 'Inspect Element'
9. In the developer panel, go to the 'Storage' tab and select 'Cookies'
10. Double-click the `uw-remember-me-[UW NetID]' entry and copy its value
11. This cookie will be valid for 1 month. To generate a fresh cookie, repeat this process

### Setting up Your Course-Hunter Email

We are unable to interact with @uw.edu email servers due to restrictions imposed by UW IT Connect.
In order to circumvent this, we will need to forward emails from the @uw.edu account to a @gmail.com
account. It is recommended that a dummy @gmail.com account is used for this purpose
1. Visit [Gmail](https://mail.google.com/) and create a new @gmail.com account (e.g. UWNetID.coursehunter@gmail.com)
2. Once set up, press the gear icon in the top-right corner and select 'See All Settings'
3. Go to the 'Forwarding and POP/IMAP' tab and select 'Enable IMAP'. Make sure to save your changes
4. Press the profile icon in the top-right corner and select 'Manage Your Google Account'
5. Go to the 'Security' tab and activate '2-Step Verification'
6. Once set up, return to the 'Security' tab and select 'App Passwords'
7. Select 'Mail' as your app and 'Mac' as your device and generate the app password
8. The program will use your email address and app password to interact with the @gmail.com email server  

### Setting up Your Credentials

Create a file named 'credentials.json' in the root directory with the following content

    {
      "uw_netid": "UW NETID",
      "uw_netid_password": "UW NETID PASSWORD",
      "uw_remember_me_cookie": "UW_REMEMBER_ME COOKIE VALUE",
    
      "gmail_user": "GMAIL ADDRESS",
      "gmail_app_password": "GMAIL APP PASSWORD"
    }

### Setting up Safari for Automation

In order to enable the program to automatically register for courses, we must allow it to control the
Safari browser
1. Select the 'Develop' menu within the Safari menu bar
2. Make sure that 'Allow Remote Automation' is ticked

### Running the Program

You're all set! Run `main.py` to start the program. You will see a browser window open and close as the
program verifies that your credentials are valid. Once verified, the program will listen for incoming
Notify.UW emails in the background. Check out console logs for any new activity