import sys
import time
import threading

class Cursor:
    def show():
        sys.stdout.write("\033[?25h")
        sys.stdout.flush()

    def hide():
        sys.stdout.write("\033[?25l")
        sys.stdout.flush()

class Spinner:
    def __init__(self, function, delay=0.1):
        self.function = function
        self.delay = delay
        self.done = False
        self.spinner_generator = self._spinning_cursor()

    def _spinning_cursor(self):
        while True:
            for cursor in '|/-\\':
                yield cursor

    def _spin(self):
        while not self.done:
            sys.stdout.write(next(self.spinner_generator))
            sys.stdout.flush()
            time.sleep(self.delay)
            sys.stdout.write('\b')

    def run(self, *args, **kwargs):
        self.done = False
        self.thread = threading.Thread(target=self._spin)
        self.thread.start()
        try:
            Cursor.hide()
            result = self.function(*args, **kwargs)
        finally:
            self.stop()
            Cursor.show()
        return result

    def stop(self):
        self.done = True
        self.thread.join()
        # sys.stdout.write('Done!\n')
        sys.stdout.write('')
        sys.stdout.flush()

# Example usage
def long_running_task(duration):
    time.sleep(duration)  # Simulate a long-running task
    return "Task Completed"

if __name__ == "__main__":
    spinner = Spinner(long_running_task)
    result = spinner.run(10)  # Pass the duration argument to the function
    print(result)