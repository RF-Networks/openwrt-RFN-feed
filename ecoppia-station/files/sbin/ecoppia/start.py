import os
import os.path
import sys

workingdir = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), 'ecoppia1')
sys.path.insert(0, workingdir)

import ecoppia.ecoppia_station

#import test_telit_commands
#import test_unit_simulator

