import time
from datetime import datetime, timedelta

from listeners.listener import Listener


# It takes about 2 seconds for the Automator to log in and fill out the SLN form
AUTOMATOR_DELAY_OFFSET = timedelta(seconds=2)


class TimeListener(Listener):

    # Initialize object and establish connection to Gmail server
    def __init__(self, automator, joint_registration_list, target_time):
        super().__init__("Time Listener", automator)

        self.target_time = target_time
        self.is_triggered = False

        # Get the first SLN code in the joint registration list
        # When Automator receives this, it will register all SLN codes in the list
        self.sln_code = joint_registration_list[0]["add"][0]

        print("Time Listener: Initialized")

    # Scans inbox for unread Notify.UW emails
    def listener_task(self):
        current_time = datetime.now()
        if not self.is_triggered and (current_time - timedelta(seconds=5)).time() < self.target_time < (current_time + AUTOMATOR_DELAY_OFFSET).time():
            print(f"Time Listener: Triggered at {datetime.now().time()}")

            self.is_triggered = True
            try:
                self.automator.register(self.sln_code)
            except Exception:
                print(f"Time Listener: Could not register since another listener is currently controlling Safari")
