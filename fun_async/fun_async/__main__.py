#pylint:disable=missing-docstring
#pylint:enable=missing-docstring


import time

from fun_async.threads.threads import ThreadingDemo


class BlockingMethod:
    """
    A method that blocks for some time
    """
    block_for = 5

    def __init__(self, uid):
        self._uid = uid

    def __call__(self):
        print(f"  {self._uid}: Started")
        time.sleep(type(self).block_for)
        print(f"  {self._uid}: Finished")

    @classmethod
    def create_methods(cls, num):
        """
        Create a list of @num BlockingMethod instances
        """
        blocking_methods = []
        for uid in range(num):
            blocking_methods.append(BlockingMethod(uid))
        return blocking_methods


def main():
    """
    Entry point for the demonstrations
    """
    threading_demo = ThreadingDemo(methods=BlockingMethod.create_methods(10))
    threading_demo.run()


if __name__ == "__main__":
    main()
