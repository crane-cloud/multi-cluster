import threading


# We can create different timer instances from this BaseTimer
class BaseTimer:
    def __init__(self, timeout, callback):
        self.timeout = timeout # duration of the timer
        self.callback = callback # function called at the end of the timer
        self.timer = threading.Timer(timeout, self._on_timeout)
        self.timer.start()

    # Reset the timer if required - for example if informMember message is received within the timer period
    def reset(self):
        self.timer.cancel()
        self.timer = threading.Timer(self.timeout, self._on_timeout)
        self.timer.start()

    # Method called when the timer expires
    # Returns the callback function
    def _on_timeout(self):
        self.callback()

    # Stop the timer if required
    def stop(self):
        self.timer.cancel()
