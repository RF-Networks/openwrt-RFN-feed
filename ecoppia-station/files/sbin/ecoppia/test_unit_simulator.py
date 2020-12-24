import os
import os.path
import sys
from rx import Observable
from rx.concurrency import *
from rx.concurrency.newthreadscheduler import *
from struct import *

workingdir = os.path.join(os.path.abspath(os.path.dirname(os.path.realpath(__file__))), 'ecoppia1')
sys.path.insert(0, workingdir)
from ecoppia.connector_wrappers.telit_le_50 import *
from ecoppia.globals import *

rf = TelitLE50("/dev/ttyS1")
rf.StartConfigMode()
rf.ResetConfiguration()
time.sleep(2)
rf.EndConfigMode()

rf.StartConfigMode()
rf.AtsCommnad(262, 3)
rf.AtsCommnad(263, 3)
rf.AtsCommnad(264, 3)
rf.AtsCommnad(202, 6)
rf.AtsCommnad(220, 9)
rf.AtsCommnad(226, 2)
rf.AtsCommnad(223, 5)
rf.AtsCommnad(255, 175)

rf.AtsCommnad(200, 5)
rf.AtsCommnad(252, 107)

rf.EndConfigMode()

obs = rf.rx_msg_subject.observe_on(Scheduler.new_thread)
for x in obs.to_blocking():
	rf.Send(x.unit_id, x.packet_id,  b'\x00\x00\x00\x00\x00\x00\x00\x00' + pack('>B', x.rssi) + pack('>H', 24000) + b'\x00\20\x00\x00')
	
sys.exit()

