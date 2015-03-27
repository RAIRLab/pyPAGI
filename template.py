import time
import math
import random
from pagi_api import *

cs = connectSocket()
agent = Agent(cs)


while True:
	#MAIN LOOP.
	
	#check any new messages that were sent
	responses = getMessages(cs)
	for r in responses:
		if r != "":
			print "Message received: " + r
			#Do anything you want with the message here...
			
			
			
	#Do whatever you want: send messages, etc.
	if random.random() < 0.1:
		agent.findObject("apple")
	else:
		print "not"
	
closeClient()

exit()