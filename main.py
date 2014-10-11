import argparse
import sys
import datacat
from datacat import Datacat

################### Start of main program ###################

# Parsing args
parser = argparse.ArgumentParser(description='Implementation for Datacat')
parser.add_argument('-f', '--filepath', nargs='?', default='no_input', 
                    help='Specify the relative path to the http log file.')
parser.add_argument('-t', '--threshold', nargs='?', default='10', 
                    help='Specify the threshold for maximum number of requests every two minutes that trigger the alert.')
args = vars(parser.parse_args())

relative_path = args['filepath']
threshold = int(args['threshold'])

if relative_path == 'no_input':
  print 'No input file, exit.'
  sys.exit() 


cat = Datacat(relative_path, threshold)
cat.run()

