#pylint:disable=missing-docstring
#pylint:enable=missing-docstring


import threading


class ThreadingDemo:
    """
    Demonstrate running concurrent tasks using Pythons builtin threading
    library.

    Args:
        methods: list of callable objects which determine the list of tasks
    """
    #pylint:disable=too-few-public-methods

    def __init__(self, methods=None):
        self._methods = methods
        self._threads = []

    def run(self):
        """
        Run the threading demo
        """
        print("Starting ThreadingDemo")
        self._create_threads()
        self._start_threads()
        self._wait_threads()
        print("Finished")

    def _create_threads(self):
        print("Creating some threads...")
        for method in self._methods:
            thread = threading.Thread(target=method)
            print(f"  {repr(thread)}")
            self._threads.append(thread)

    def _start_threads(self):
        print("Starting all threads...")
        for thread in self._threads:
            thread.start()

    def _wait_threads(self):
        print("Waiting for all threads to complete...")
        for thread in self._threads:
            thread.join()
