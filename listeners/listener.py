from threading import Thread


# Listener interface
class Listener:

    SLN_REGEX = "SLN: ([0-9]{5})"

    def __init__(self, name, automator):
        self.name = name
        self.automator = automator

        self.thread = None
        self.is_running = False

    # Constantly executes listener_task()
    def listener(self, is_running):
        while is_running():
            self.listener_task()

    # Implement listener here
    def listener_task(self):
        pass

    # Starts listener in a new thread
    def start(self):
        if self.thread is not None or self.is_running:
            print(f"{self.name}: Already listening")
            return

        self.is_running = True
        self.thread = Thread(target=self.listener, args=(lambda: self.is_running,))
        self.thread.start()
        print(f"{self.name}: Started listening")

    # Stops listener
    def stop(self):
        if self.thread is None or not self.is_running:
            print(f"{self.name}: Already stopped listening")
            return

        self.is_running = False
        self.thread.join()
        self.thread = None
        print(f"{self.name}: Stopped listening")
