import time
import math
import random
from pagi_api import *

cs = connectSocket()

#if you leave it blank, it will try to find the IP itself. Otherwise, you can
#type in an IP manually:
#cs = connectSocket(ip="128.113.243.43")

#you can also type a port if you're not using the default 42209:
#cs = connectSocket(ip="128.113.243.43", port=230)

#create an agent and bind it to the port you just opened
agent = Agent(cs)

#agent.loadTask("ACE_task")
#agent.createItem("Assets/cat.jpeg", 3.0, 2.0, 0.0, "cat0", 2, 0.0, 10.10, 3)
#time.sleep(0.001)
#responses = getMessages(cs)
#for r in responses:
#    if r != "":
#        print "Message received: " + r

agent.createItem("cat.jpeg", 3.0, -20.0, 0.0, "cat1", 2, 0.0, 10.10, 3)
time.sleep(0.001)
responses = getMessages(cs)
for r in responses:
    if r != "":
        print "Message received: " + r

agent.createItem("/Users/Erickson656/Documents/GitHub/PAGIworld/source/Assets/garf.jpg", 3.0, 0.0, 0.0, "cat2", 2, 0.0, 10.10, 0)
time.sleep(0.001)
responses = getMessages(cs)
for r in responses:
    if r != "":
        print "Message received: " + r

agent.say("Hello cats!",10,10.0,10.0,'P')
time.sleep(0.001)

#while True:
	#MAIN LOOP.

	#check any new messages that were sent
#	responses = getMessages(cs)
#	for r in responses:
#		if r != "":
#			print "Message received: " + r
			#Do anything you want with the message here...
        
	#Do whatever you want: send messages, etc.
	#here we make him jump with probability 10%, otherwise we print "not".
	# if random.random() < 0.1:
	# 	#agent.findObject("apple")
	# 	agent.jump()
	# else:
	# 	print "not"

closeClient(cs)

exit()
