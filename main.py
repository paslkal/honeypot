from honeypot import Honeypot
import threading
import time


def main():
    honeypot = Honeypot()

    # Start listeners for each port in separate threads
    for port in honeypot.ports:
        listener_thread = threading.Thread(target=honeypot.start_listener, args=(port,))
        listener_thread.daemon = True
        listener_thread.start()

    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down honeypot...")
        exit(0)


if __name__ == "__main__":
    main()
