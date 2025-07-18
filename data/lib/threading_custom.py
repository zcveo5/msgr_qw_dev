import threading

stop_safe_threads = False

def safe_thread(target, **args):
    while not stop_safe_threads:
        target(**args)
    else:
        return


def create_thread(target, **args):
    return threading.Thread(target=lambda: safe_thread(target, **args))


def is_all_threads_stopped():
    for thread in threading.enumerate():
        if thread != threading.main_thread() and thread.is_alive():
            return False
    return True

