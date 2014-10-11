import datacat
from datacat import Datacat
import threading
import sys
import time

def mock_hit_on_section(log_file, hits, gap):
    file_out = open(log_file, 'w')
    for i in xrange(hits):
        time.sleep(gap)
        file_out.write('127.0.0.1 - - [09/Oct/2014:17:23:05 -0400] "GET /examples/ HTTP/1.1" 304 -\n')
            
## Creat a sample test file.
def test_1():
    print 'Test case 1 started.'
    print 'Threshold value: 20'
    print 'Fake User, 1 hit per 0.5 second, totally 21 hits'
    print 'This test case takes 5 seconds.'

    test_file = open('test_datacat.txt', 'w')
    test_file.write('127.0.0.1 - - [09/Oct/2014:09:30:51 -0400] "GET /dummy/ HTTP/1.1" 200 11217')
    test_file.close()

    cat = Datacat('test_datacat.txt', 20,testing=True)
    cat.daemon = True
    cat.start()
    
    if cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should not be alerting at this stage\n'
        return 0

    mock_hit_thread = threading.Thread(target=mock_hit_on_section,
                                       args=['test_datacat.txt', 21, 0.1])
    mock_hit_thread.daemon = True
    mock_hit_thread.start()
    time.sleep(5)   
 
    if not cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should be alerted at this time.\n'
        return 0

    cat.signal_stop() 
    print 'Test case (1) succeeded.\n'
    return 1


## Creat a sample test file.
def test_2():
    print 'Test case 2 started.'
    print 'Threshold value: 100'
    print 'Fake User, 1 hit per 0.5 second, totally 101 hits'
    print 'This test case takes around 60 seconds.'

    test_file = open('test_datacat.txt', 'w')
    test_file.write('127.0.0.1 - - [09/Oct/2014:09:30:51 -0400] "GET / HTTP/1.1" 200 11217')
    test_file.close()

    cat = Datacat('test_datacat.txt', 100, testing=True)
    cat.daemon = True
    cat.start()
    
    if cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should not be alerting at this stage\n'
        return 0

    mock_hit_thread = threading.Thread(target=mock_hit_on_section,
                                       args=['test_datacat.txt', 101, 0.5])
    mock_hit_thread.daemon = True
    mock_hit_thread.start()
    time.sleep(60)   
 
    if not cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should be alerted at this time.\n'
        return 0

    cat.signal_stop() 
    print 'Test case (2) succeeded.\n'
    return 1
   
   
## Creat a sample test file.
def test_3():
    print 'Test case 3 started.'
    print 'Threshold value: 100'
    print 'Fake User, 1 hit per 1 second, totally 101 hits'
    print 'This test case takes around 110 seconds.'
    print 'You are expected to see the recovered message at the end'

    test_file = open('test_datacat.txt', 'w')
    test_file.write('127.0.0.1 - - [09/Oct/2014:09:30:51 -0400] "GET / HTTP/1.1" 200 11217')
    test_file.close()

    cat = Datacat('test_datacat.txt', 100,testing=True)
    cat.daemon = True
    cat.start()
    
    if cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should not be alerting at this stage\n'
        return 0

    mock_hit_thread = threading.Thread(target=mock_hit_on_section,
                                       args=['test_datacat.txt', 101, 1])
    mock_hit_thread.daemon = True
    mock_hit_thread.start()
    time.sleep(120)   
 
    if not cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The cat should be alerted at this time.\n'
        return 0
    time.sleep(10)
    if cat.alerting:
        cat.signal_stop()
        print 'Test case failed. The alert should be recovered now\n'
        return 0

    cat.signal_stop() 
    print 'Test case (3) succeeded.\n'
    return 1
 
################# Main Program for Datacat Test ######################
from subprocess import call
call(['rm', 'test_datacat.txt'])
print 'Test file removed'

test_cases = [test_1, test_2, test_3]
count = 0
for proc in test_cases:
    if proc():
        count += 1
print count, ' out of ', len(test_cases), ' passed!'
sys.exit(0)









