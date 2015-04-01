import socket
import time
import math
import sys
import random
import select
import threading
import thread

#connects the socket. Returns the socket that you will need.
def connectSocket(ip=None,port=42209):
    # connect to local address
    if ip==None:
    	IP_ADDRESS = socket.gethostbyname(socket.gethostname())
    else:
        IP_ADDRESS = ip
    clientsocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clientsocket.connect((IP_ADDRESS, port))
    clientsocket.setblocking(0)
    return clientsocket


def closeClient(clientsocket):
    """
	Closes connection to PAGI World; must be called to interact with pagi_api outside of pagi_api.py
	"""
    clientsocket.close()


unread = []  # stores all unread messages from socket


def send(msg, clientsocket):
    '''
	WARNING: seems to randomly ignore responses from the socket, causing an infinite loop
	(possibly) PREVENTS clientsocket.recv FROM WORKING OUTSIDE THIS FUNCTION
	calls socket.send(out) and returns corresponding value of socket.recv()
	waits for socket to respond before exiting
	'''
    # send message
    clientsocket.send(msg)  # , clientsocket)


# messageType = msg.split('\n')[0].split(',')[1]
# 
# 	global unread
# 	while True:
# 		# update unread with responses from socket
# 		readable = select.select([clientsocket], [], [], 1)
# 		if readable[0]:
# 			# read message and add to messages
# 			responses = clientsocket.recv(8192).split('\n')	# limit of 8192 characters
# 			for response in responses:
# 				if response != "":
# 					unread.append(response)
# 
# 		# search unread messages for match with current call; remove and return if found
# 		for message in unread:
# 			responseType = message.split(',')[0]
# 			if responseType == messageType:
# 				unread.remove(message)
# 				return message

#socket = socket object to send to
#timeout = timeout, in ms
def getMessages(socket):
    readable = select.select([socket], [], [], 0.25)  #timeout/1000)
    if readable[0]:
        # read message and add to messages
        responses = socket.recv(8192).split('\n')  # limit of 8192 characters
        return responses
    return []


class Body:
    '''
	UNIMPLEMENTED
	holds body sensors 
	'''

    def __init__(self, socket):
        self.sensors = []
        self.clientsocket = socket

    def getSensor(self, num=None):
        '''
		Returns the numth body sensor reading. If num is unspecified, returns a list of
		all body sensor readings. 0 is top, increases counterclockwise.
		'''
        pass


class Hand:
    def __init__(self, handStr, socket):
        if handStr != "R" and handStr != "L":
            print "ERROR: invalid handStr value. Expected 'R' or 'L', instead found", handStr
            return
        self.hand = handStr
        self.closed = False
        self.holdingObj = False
        self.sensors = []
        self.clientsocket = socket


    def getCoordinates(self):
        '''
		returns x and y coordinates of hand relative to body
		'''
        curLoc = send('sensorRequest,' + self.hand + 'P\n', self.clientsocket)
        tmp = curLoc.split("\n")[0].split(",")
        x = float(tmp[1])
        y = float(tmp[2])
        return x, y

    def sendForce(self, x, y):
        if self.hand == "R":
            send('addForce,RHvec,' + str(x) + ',' + str(y) + '\n', self.clientsocket)
        else:
            send('addForce,LHvec,' + str(x) + ',' + str(y) + '\n', self.clientsocket)

    def getDist(self, x, y):
        '''
		get distance from position x.y
		'''
        curX, curY = self.getCoordinates()
        #print str(curX) + "," + str(curY), "to", str(x) + "," + str(y)
        return ((curX - x) ** 2 + (curY - y) ** 2) ** 0.5


    # 	def moveHand(self, x, y, tolerance = 1.5):
    # 		'''
    # 		move to point x.y within a specified tolerance
    # 		WARNING: If it is impossible to move to x.y, this will infinite loop
    # 		TODO: keep track of how long you've been waiting so you can fix that
    # 		'''
    # 		# convert x, y from Unity item units (whatever they are) to detailed vision units (0.0 - 30.20)
    # 		x = -2.25 + float(x)*0.148
    # 		y = 1.65 + float(y)*0.1475
    #
    # 		h = self.hand
    #
    # 		# Keep a copy of unread to revert to, since this does not use send(). Oherwise, a huge number of
    # 		# useless results would end up in unread
    # 		global unread
    # 		unreadCpy = unread
    #
    # 		# move hand in x and y directions
    # 		# WARNING: randomly causes problems with send(). Might be fixed; it is a bit random.
    # 		#    note that this is likely caused by not recieving the socket data for the reflex functions,
    # 		#    clogging up the socket's responses in send()
    # 		clientsocket.send('setReflex, ' +
    # 			'lock' + h + 'X,' +
    # 			h + 'Px|!|' + str(x) +
    # 			',sensorRequest|' + h + 'P;addForce|' + h + 'HH|[350*(' + str(x) + '-' + h +'Px)]\n'
    # 			, self.clientsocket)
    # 		clientsocket.send('setReflex, ' +
    # 			'lock' + h + 'Y,'
    # 			+ h + 'Py|!|' + str(y)
    # 			+ ',sensorRequest|' + h + 'P;addForce|' + h + 'HV|[350*(' + str(y) + '-' + h +'Py)]\n')
    #
    # 		# wait until sufficiently close, then return
    # 		while self.getDist(x, y) > tolerance:
    # 			#print "dist:", self.getDist(x, y)
    # 			time.sleep(0.5)
    # 		unread = unreadCpy



    def grab(self):
        '''
		apply grabbing force and update holding status
		'''
        send('addForce,' + self.hand + 'HG,5\n', self.clientsocket)
        response = send('sensorRequest,' + self.hand + '2', self.clientsocket).split(',')[1]
        self.closed = True
        if response == "1":
            self.holdingObj = True


    def release(self):
        '''
		stop appliying grabbing force and update holding status
		'''
        response = send('addForce,' + self.hand + 'HR,5\n', self.clientsocket)
        self.closed = False
        self.holdingObj = False


class GameObject:
    '''
	contains data of objects encountered on Unity side
	may be expanded to contain additional data
	'''

    def __init__(self, objName, x, y, movement):
        self.name = objName
        self.x = x
        self.y = y
        self.moving = movement


class Vision:
    '''
	TODO: consider storing self.objects as a dictionary for faster retrieval
	and just generally clean up this mess...
	'''

    def __init__(self, socket):
        self.clientsocket = socket
        self.vision = []
        self.objects = []
        self.update()

    def update(self, vtype='detailed'):
        # set vtype to detailed if invalid (may not properly check for validity...)
        if not isinstance(vtype, str) or not vtype == 'detailed' or not vtype == 'peripheral':
            vtype = 'detailed'

        # get number of pixels read by sensor
        x0, y0 = 0, 0
        if vtype == 'detailed':
            x0, y0 = 31, 21
        else:
            x0, y0 = 16, 11

        # get sensor reading
        totalChars = 0
        counter = 0
        a = send('sensorRequest,MDN\n', self.clientsocket)
        visionOutput = a.split('\n')[0]
        visionList = visionOutput.split(",")

        # store contents of sensor reading (update self.vision)
        # TODO: consider simply overwriting contents of self.vision, rather than deleting
        #       and then entirely rewriting the list
        del self.vision[:]
        counter = 1  #skip the MDN return
        for y in range(y0):
            tempList = []
            for x in range(x0):
                tempList.append(visionList[counter])
                counter += 1
            self.vision.append(tempList)

        # update objects in vision
        tmpObjects = []
        for y in range(y0):
            for x in range(x0):
                objName = self.get(x, y)
                # if object at current pixel
                if objName != "":
                    if tmpObjects.count(objName) == 0:  #if we havent already located
                        xLoc, yLoc = self.locateObj(objName, x0, y0)  #locate the obejct
                        tmpObjects.append(objName)  #add it to the tmpObjects
                        newObject = True
                        for i in range(len(self.objects)):
                            if self.objects[i].name == objName:
                                newObject = False
                        if newObject == True:  #object is new
                            gameObj = GameObject(objName, xLoc, yLoc, True)
                            self.objects.append(gameObj)
                        else:  #object has been here, check if it has moved
                            for i in range(len(self.objects)):
                                if self.objects[i].name == objName:
                                    if xLoc == self.objects[i].x and yLoc == self.objects[i].y:  #hasnt moved
                                        self.objects[i].moving = False
                                        break
                                    else:  #has moved
                                        self.objects[i].moving = True
                                        self.objects[i].x = xLoc
                                        self.objects[i].y = yLoc
                                        break

        # delete objects no longer in field of view
        i = 0
        while i < len(self.objects):
            stillInVision = False
            for j in range(len(tmpObjects)):
                if self.objects[i].name == tmpObjects[j]:
                    stillInVision = True
            if stillInVision == False:
                del self.objects[i]
                i -= 1
            i += 1


    def get(self, x, y):
        return self.vision[y][x]


    def getObject(self, name):
        '''
		returns full GameObject that has the given name
		'''
        for item in self.objects:
            if item.name == name:
                return item
        return None


    def printObjects(self):
        print "========Object Print========"
        for i in range(len(self.objects)):
            print "Object " + str(i) + ":"
            print "\tName: " + self.objects[i].name
            print "\tCoordinates: (" + str(self.objects[i].x) + "," + str(self.objects[i].y) + ")"
            print "\tMoving: " + str(self.objects[i].moving)


    def locateObj(self, object, x0, y0):
        '''
		what does this do?...
		'''
        numCoords = 0
        xSum = 0
        ySum = 0
        for y in range(y0):
            for x in range(x0):
                if (self.get(x, y) == object):
                    xSum += x
                    ySum += y
                    numCoords += 1
        if numCoords == 0:
            return null

        xCoord = xSum / numCoords
        yCoord = ySum / numCoords

        returnValue = xCoord, yCoord
        return returnValue


#==================================================================
#===============================AGENT==============================
#==================================================================
class Agent:
    def __init__(self, socket):
        self.clientsocket = socket
        self.lhand, self.rhand = Hand("L", self.clientsocket), Hand("R", self.clientsocket)
        #self.vision = Vision(self.clientsocket)
        self.body = Body(self.clientsocket)

    def findObject(self, objName):
        self.clientsocket.send("findObj," + objName + ",P")
        readable = select.select([self.clientsocket], [], [], 0.25)  #timeout/1000)
        if readable[0]:
            # read message and add to messages
            responses = self.clientsocket.recv(8192).split('\n')  # limit of 8192 characters
            #responses = [c for c in responses if c != ""]
            responses = responses[0].split(',')[2:]
            responses = [c for c in responses if c != ""]
            print responses

    def sendForce(self, x, y):
        send('addForce,BMv`ec,' + str(x) + ',' + str(y) + '\n', self.clientsocket)

    def jump(self):
        response = send('addForce,J,30000\n', self.clientsocket)


    def resetRotation(self):
        'resets rotation to 0 degrees; this can also be accomplished by passing rotate() 0 as its val parameter'
        r = self.getRotation()
        self.rotate(0)


    def getRotation(self, degrees=True):
        'Returns the rotation of the agent in radians by default. specifying False for radians returns rotation in degrees'
        #Error checking, setting default to return rotation in degrees
        if not isinstance(degrees, bool):
            degrees = True

        rotation = float(send('sensorRequest,A\n', self.clientsocket).split(',')[1])
        if degrees:
            return (rotation * 180 / math.pi) % 360
        else:
            return rotation % (2 * math.pi)


    def rotate(self, val, degrees=True, absolute=True):
        '''
		rotates agent to specified angle							  0
		takes degrees or radians								90  Agent  270
		absolute == True: 0 is to top of screen						 180
		absolute == False: 0 is where agent is currently facing 
		'''
        #Error checking, setting defaults to degrees and absolute direction
        if not isinstance(degrees, bool): degrees = True
        if not isinstance(absolute, bool): absolute = True

        # convert to degrees
        if not degrees:
            val = val * 180 / math.pi

        # convert global direction to relative direction
        if absolute:
            val -= self.getRotation()

        val %= 360
        send('addForce,BR,' + str(val) + '\n', self.clientsocket)
        send('addForce,LHH,0.01\n', self.clientsocket)
        send('addForce,RHH,0.01\n', self.clientsocket)


    def moveH(self, paces=1, direction='right'):
        'Moves the agent however many paces specified where one pace equals the width of the body of the agent'
        #Error checking, setting default direction to right and paces to 1
        if direction == None: direction = 'right'
        if not isinstance(direction, str) and not direction.upper() == 'RIGHT' and not direction.upper() == 'LEFT':
            direction = 'right'
        if not isinstance(paces, int):
            paces = 1

        for i in range(paces):
            if direction.upper() == 'RIGHT':
                response = send('addForce,BMH,' + str(10800) + '\n', self.clientsocket)
            else:
                response = send('addForce,BMH,' + str(-10800) + '\n', self.clientsocket)
            time.sleep(1.1)


        # 	def grabObj(self, objectName, hand = None, tolerance = 1.5):
        # 		'''
        # 		Moves specified hand to object with given name and grabs. If no hand is specified, uses the
        # 		close one. If chosen hand is already holding something, it is released before moving to the
        # 		new object.
        # 		'''
        # 		# gather object data
        # 		goalObject = self.vision.getObject(objectName)
        # 		x = goalObject.x
        # 		y = goalObject.y
        #
        # 		# select which hand to use
        # 		if hand is None:
        # 			if x < 15:
        # 				hand = "L"
        # 			else:
        # 				hand = "R"
        # 		if hand == "L":
        # 			handObj = self.lhand
        # 		elif hand == "R":
        # 			handObj = self.rhand
        # 		else:
        # 			print "WARNING: Invalid hand value for Agent.grabObj(). Expected 'L' or 'R', instead found", hand
        #
        # 		# move to object and grab
        # 		handObj.release()
        # 		handObj.moveHand(x, y, tolerance)
        # 		time.sleep(3)
        # 		handObj.grab()


    def bringHandClose(self, leftOrRight):
        """
		UNIMPLEMENTED
		bring specified hand close to body
		"""
        if leftOrRight == "R":
            pass
        elif leftOrRight == "L":
            pass
        else:
            print "ERROR: invalid argument in Agent.bringHandClose. Expected 'L' or 'R', instead found", leftOrRight