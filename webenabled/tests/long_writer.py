#
# Test program that we can spin off into it's own sub process which
# then opens a file and (slowly) writes into it.  That will allow us
# to test whether or not we can determine when a process is accessing
# a file.
import time

LONG_FILE_PATH = "/tmp/long_writer_file.txt"



def open_and_write_a_file():
    print(f"Started long_writer. sleeping for 2 seconds ")
    time.sleep(2)

    print(f"Opening and starting to write to {LONG_FILE_PATH} for 2 seconds")
    with open(LONG_FILE_PATH, 'a') as file:
        for x in range(0, 20):
            file.write("some stuff")
            time.sleep(0.1)
    print(f"done writing to file ")

    print(f"waiting for 2 seconds for ending")
    time.sleep(2)

if __name__ == '__main__':
    open_and_write_a_file()
