from subprocess import Popen, PIPE
import time


def handle_results(output):
    print output

running_procs = [
    Popen(['mitmdump','-p','8090'], stderr=PIPE)
    for path in '/tmp/file0 /tmp/file1 /tmp/file2'.split()]

while running_procs:
    for proc in running_procs:
        retcode = proc.poll()
        if retcode is not None: # Process finished.
            running_procs.remove(proc)
            break
    else: # No process is done, wait a bit and check again.
        time.sleep(.1)
        continue

    # Here, `proc` has finished with return code `retcode`
    if retcode != 0:
        """Error handling."""
    handle_results(proc.stdout)



