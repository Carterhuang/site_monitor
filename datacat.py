import time
import threading
import sys
import os
import signal

## A global function that retrieves the section information
## from one row of w3c http log.
def retrieve_section(line):
    parts = line.split()
    ## Not an valid log format.
    if len(parts) < 10:
        return None
    ## The hit is not successful.
    status = int(parts[8])
    if status > 400:
        return None
    section = parts[6].split('/')[1]
    return section


class Datacat(threading.Thread):

    """    
        A customizable Datacat constructor. Users can set the threshold 
        of hits over two minutes that trigger an alert. 
    """
    def __init__(self, file_name, threshold=10, testing=False):
        threading.Thread.__init__(self)

        ## a thread-safe dictionary guarded by the lock below.
        ## The dictionary keeps track of how many hits are recorded
        ## for one section.
        self.entry_map = {}

        self.file_path = os.path.abspath(file_name)

        ## a lock variable to secure entry_map is thread-safe.
        self.lock = threading.Lock()

        self.threshold = threshold
        self.event_queue = []
        self.alerting = False

        ## a volatile flag variable to signal if the main thread
        ## should continue.
        self.stopping = False

        ## a flag set for testing mode, if this flag is on, less i/o
        ## is generated and flushed into the pipeline. Specially, only
        ## alert information will be printed.
        self.testing = testing


    """
        In run(), is thread is allowcated for this function.
        A function that calls display_popular_hit every 10 seconds.
    """
    def monitor_10sec(self):
        while 1:
            time.sleep(10)
            self.display_popular_hit()

    
    """
        A subroutine that displays the most popular hit every second.
        Meanwhile, if an alert has been triggered for exceedingly high traffic,
        once the traffic goes down again, this function prints a "Recovered" to
        to the terminal.
    """
    def display_popular_hit(self):
        with self.lock:
            popular = ''
            hits = -1
            for k in self.entry_map.keys():
                if hits < self.entry_map[k]:
                    hits = self.entry_map[k]
                    popular = k
            if not self.testing:
                output = ''.join(['Most popular: ', popular, '\nHits: ', str(hits), '\n'])
                sys.stdout.write(output) 
            if time.time() - self.event_queue[0][0] >= 120 and self.alerting:
                sys.stdout.write("Recovered!!!!!!!!\n")
                sys.stdout.flush()
                self.alerting = False


    """
        A function that updates number of hits corresponding to one section.
    """
    def update_entry_map(self, sec):
        if sec == None:
            return
        if sec not in self.entry_map:
            self.entry_map[sec] = 0
        else:
            self.entry_map[sec] += 1

    """
        A thread is allowcated for this function. 
        This function read an actively written to file as input. Then it takes
        any newly written line, update section-hits map(entry_map) and closely
        watch for the traffic. If traffic is two high, it triggers an alarm. 
    """
    def load_file(self):

        ## A queue used for monitoring traffic over two minutes.
        ## The logic is mainly explained in README, the design doc.
       
        file_in = open(self.file_path, 'r')
        initial_time = int(time.time())
        self.event_queue.append((initial_time, 'dummy_section'))
        line = file_in.readline()
        while line:
            sec = retrieve_section(line)
            self.update_entry_map(sec)
            line = file_in.readline()
        
        while 1:
            where = file_in.tell()
            line = file_in.readline()
            if not line:
                time.sleep(0.1)
                file_in.seek(where)
            else:
                sec = retrieve_section(line)
                self.update_entry_map(sec)

                if len(self.event_queue) < self.threshold:
                    self.event_queue.append((int(time.time()), sec))
                else:
                    ## This section is for the alerting logic.
                    current_time = int(time.time())
                    head = self.event_queue.pop(0)
                    self.event_queue.append((current_time, sec))
                    if current_time - head[0] < 120:
                        formatted = time.strftime('%m/%d/%Y %H:%M:%S', time.gmtime(head[0]))
                        out = ''.join(["Alert! High traffic at ...\n", formatted, '\n'])
                        sys.stdout.write(out)
                        sys.stdout.flush()
                        self.alerting = True
                    elif self.alertingi and self.event_queue[0][0] - current_time > 120:
                        sys.stdout.write("Recovered!!!!!!!!!!\n")
                        sys.stdout.flush()
                        self.alerting = False
 
    """
        Set stopping to true to signal stop
        in the while loop.    
    """
    def signal_stop(self):
        self.stopping = True


    """
        Function to intialize the entire monitoring processes.
        It allowcates two other threads for reading file and
        displaying results.

        This process termintes when a Ctrl - C is deteced or 
        the testing framework calles stop().
    """
    def run(self):
        sys.stdout.write('Datacat wakes up ... \n')
        sys.stdout.flush()

        load_file_daemon = threading.Thread(target=self.load_file)
        monitor_thread = threading.Thread(target=self.monitor_10sec)
        load_file_daemon.daemon = True
        monitor_thread.daemon = True

        load_file_daemon.start()
        monitor_thread.start()

        try:
            while 1:
                ## Waiting for the Ctrl - C exit signal.
                if self.stopping:
                    print 'Datacat goes to sleep ...\n'
                    return;
        except KeyboardInterrupt:
            print 'Datacat goes to sleep ...\n'
