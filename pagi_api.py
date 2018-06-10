""" This is the main api for use with PAGI-World
    It contains many prewritten classes and functions that can help serve
    as a starting point for the creation of agents to use in PAGI-World or
    for getting an understanding of the PAGI-World environment.

    The ACE-Test.py python script will run through all available commands, and
    is a good place to look to see examples of the API in action.
    (Note you will have to change the IP address at the top of the file to the
    appropriate number, and have the PAGI-World server running at a reachable address.

    The template.py serves as a barebones template for setting up an agent to
    interact in the PAGI-World environment.

    Last Updated - 3/20/2018 by Austin Erickson
"""
import socket
import time
import math
import sys
import random
import select
import threading
import thread
import json

# a variable that controls how long to wait (in seconds) for sensor data from unity
# a lower value speeds up response time, but risks not receiving data from unity
sleepPause = 0.0001

# if waitForData is True requests for sensor data and information from PAGI world will
# wait until the requested data is retrieved.
# if set to false, it will wait for the duration specified in sleepPause, then will move on.
waitForData = True

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

""" This function is used to generate a json string containing a command to be sent to PAGI-World
    MessageType, stringContent are strings
    floatContent, vecX, and vecY and floats
    otherstrings is a list of strings (separated by commas)
    messages is a list of commands that contain other messges/commands (separated by commas)
        NOTE that each command in the list should start with '{' and end with '}'
        No additional quotes should be inserted at the beginning or end of the object/string
    See the PAGI-World documentation for more info on formatting messages/commands to PAGI """
def toJson(messageType,stringContent,floatContent,vecX,vecY,otherStrings,lenOtherStrings,messages,lenMessages):
    newstr = '{"messageType":"' + messageType + '","stringContent":"' + stringContent + '","floatContent":' + \
             str(floatContent) + ',"vectorContent":{"x":' + str(vecX) + ',"y":' + str(vecY) + '},"otherStrings":['
    for i in range(lenOtherStrings):
        if i != 0:
            newstr = newstr + ','
        newstr = newstr + '"' + otherStrings[i] + '"'
        i = 1
    newstr = newstr + '],"messages":['
    for i in range(lenMessages):
        if i != 0:
            newstr = newstr + ','
        newstr = newstr + messages[i]
    newstr = newstr + ']}\n'
    return newstr


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
        send('{"messageType":"sensorRequest","stringContent":"' +
             self.hand + 'P","floatContent":0.0,"vectorContent":{"x":0.0,"y":0.0},"otherStrings":[],"messages":[]}\n',
             self.clientsocket)
        curLoc = getMessages(self.clientsocket)
        tmp = json.loads(curLoc)

        x = float(tmp["x"])
        y = float(tmp["y"])
        return x, y

    def sendForce(self, x, y):
        if self.hand == "R":
            s = toJson("addForce","RHvec",0.0,str(x),str(y),"",0,"",0)
            send(s,self.clientsocket)
        else:
            s = toJson("addForce", "LHvec", 0.0, str(x), str(y), "", 0, "", 0)
            send(s, self.clientsocket)

    def getDist(self, x, y):
        '''
        get distance from position x.y
        '''
        curX, curY = self.getCoordinates()
        #print str(curX) + "," + str(curY), "to", str(x) + "," + str(y)
        return ((curX - x) ** 2 + (curY - y) ** 2) ** 0.5


    #   def moveHand(self, x, y, tolerance = 1.5):
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
        s = toJson("addForce", self.hand + 'HG', 0.0, 5.0, 0.0, "", 0, "", 0)
        send(s, self.clientsocket)
        response = getMessages(self.clientsocket) # grab the update
        json_data = json.load(response)
        number = json_data["content"].split(',')[1]
        if number == "1" :
            self.closed = True
        print response

        s = toJson("sensorRequest", self.hand + '2', 0.0, 0.0, 0.0, "", 0, "", 0)
        send(s, self.clientsocket)
        response = getMessages(self.clientsocket)
        json_data = json.load(response)[0]
        number = json_data["p"]

        if number == "1":
            self.holdingObj = True


    def release(self):
        '''
		stop appliying grabbing force and update holding status
		'''
        s = toJson("addForce", self.hand + 'HG,', 0.0, 5.0, 0.0, "", 0, "", 0)
        send(s, self.clientsocket)
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
            code = "MDN"
            x0, y0 = 31, 21
        else:
            code = "MPN"
            x0, y0 = 16, 11

        # get sensor reading
        totalChars = 0
        counter = 0

        s = toJson("sensorRequest", code, 0.0, 0.0, 0.0, "", 0, "", 0)
        send(s, self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            a = getMessages(self.clientsocket)
            found = 0
            for i in a:
                if i != "":
                    json_data = json.loads(i)
                    if "type" in json_data:
                        if json_data["type"] == code:
                            found = 1
                            break
            if not waitForData:
                break

        if found == 1 and "content" in json_data:
            visionOutput = json_data["content"]
            visionList = visionOutput.split(",")
        else:
            print "Error: No detailed sensor map data retrieved!"
            return None

        # store contents of sensor reading (update self.vision)
        # TODO: consider simply overwriting contents of self.vision, rather than deleting
        #       and then entirely rewriting the list
        del self.vision[:]
        counter = 0  #skip the MDN return (NO MORE MDN RETURN TO WORRY ABOUT, CHANGED FROM 1 to 0)
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
        s = toJson("findObj", objName, 0.0, 0.0, 0.0, "P", 1, "", 0)
        send(s, self.clientsocket)
        readable = select.select([self.clientsocket], [], [], 0.25)  #timeout/1000)
        if readable[0]:
            # read message and add to messages
            responses = self.clientsocket.recv(8192).split('\n')  # limit of 8192 characters
            #responses = [c for c in responses if c != ""]
            responses = responses[0].split(',')[2:]
            responses = [c for c in responses if c != ""]
            print responses

    def sendForce(self, x, y):
        s = toJson("addForce", "BMvec", 0.0, str(x), str(y), "", 0, "", 0)
        send(s, self.clientsocket)

    def jump(self):
        s = toJson("addForce", 'J', 0.0, 30000.0, 0.0, "", 0, "", 0)
        send(s, self.clientsocket)

    def resetRotation(self):
        'resets rotation to 0 degrees; this can also be accomplished by passing rotate() 0 as its val parameter'
        #r = self.getRotation()
        self.rotate(0)

    # returns the current rotation of the PAGI guy, or None if it was not returned in
    # the time specified by sleepPause
    def getRotation(self, degrees=True):
        'Returns the rotation of the agent in radians by default. specifying False for radians returns rotation in degrees'
        #Error checking, setting default to return rotation in degrees
        if not isinstance(degrees, bool):
            degrees = True

        s = toJson("sensorRequest", 'A', 0.0, 0.0, 0.0, [], 0, [], 0)
        send(s, self.clientsocket)

        # wait to get response from unity
        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            msg = getMessages(self.clientsocket)
            # loop through the messages in the queue and see if there's a response
            # containing the current rotation
            for i in msg:
                if i != "":
                    print i
                    json_data = json.loads(i)
                    if "type" in json_data:
                        if json_data["type"] == "A":
                            rotation = json_data["x"]
                            if degrees:
                                return (rotation * 180 / math.pi) % 360
                            else:
                                return rotation % (2 * math.pi)
            if not waitForData:
                break

        print "Error: No rotation message received from unity."
        return None




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
        s = toJson("addForce", 'BR', 0.0, str(val), 0.0, [], 0, [], 0)
        send(s, self.clientsocket)
        time.sleep(sleepPause)



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
                s = toJson("addForce", 'BMH', 0.0, str(10800.0), 0.0, "", 0, "", 0)
                send(s, self.clientsocket)
            else:
                s = toJson("addForce", 'BMH', 0.0, str(-10800), 0.0, "", 0, "", 0)
                send(s, self.clientsocket)


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

    # returns a tuple of x, y velocities
    def getVelocity(self):
        s = toJson("sensorRequest", 'S', 0.0, 0.0, 0.0, [], 0, [], 0)
        send(s, self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        found = 0
        while 1:
            # now receive the info from the PAGI env
            msg = getMessages(self.clientsocket)
            for i in msg:
                if i != "":
                    print i
                    json_data = json.loads(i)
                    if "type" in json_data:
                        if json_data["type"] == "S":
                            x = json_data["x"]
                            y = json_data["y"]
                            return x,y
            if not waitForData:
                break

        print "Error: No velocity data retrieved from PAGI World"
        return None

    def addForceToItem(self,itemName,xForce,yForce):
        s = toJson("addForceToItem",itemName,0.0,xForce,yForce,[],0,[],0)
        send(s,self.clientsocket)

    # this creates a custom item in the pagi env
    def createItem(self,filePath,mass,xpos,ypos,name,ph,r,e,k):
        str1 = [ (name + "," + str(ph) + "," + str(r) + "," + str(e) + "," + str(k)) ]
        s = toJson("createItem",filePath,mass,xpos,ypos,str1,1,[],0)
        send(s,self.clientsocket)

    def destroyItem(self,name):
        s = toJson("destroyItem",name,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

    def dropItem(self,name,xpos,ypos,note):
        s = toJson("dropItem",name,0.0,xpos,ypos,[note],1,[],0)
        send(s,self.clientsocket)

    # this returns a json string containing information about the specified item
    def getInfoAboutItem(self,name):
        s = toJson("getInfoAboutItem",name,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            r = getMessages(self.clientsocket)
            for msg in r:
                if msg != "":
                    print msg
                    json_data = json.loads(msg)
                    if "name" in json_data:
                        return msg
            if not waitForData:
                break
        # no data was found in the specified time frame
        return None

    """ returns a json string containing the active reflexes or None,
        if nothing could be retrieved in the time specified by sleepPause """
    def getReflexes(self):
        s = toJson("getReflexes","",0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            r = getMessages(self.clientsocket)
            for msg in r:
                if msg != "":
                    print msg
                    json_data = json.loads(msg)
                    if "type" in json_data:
                        if json_data["type"] == "activeReflexes":
                            return msg
            if not waitForData:
                break
        print "Error: Could not retrieve reflexes from PAGI world"
        return None

    """ This removes an active reflex from the PAGI world environment """
    def removeReflex(self,name):
        s = toJson("removeReflex",name,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

    """ This assumes 'conditions' is a string containing the conditions separated by semicolons
        and that actions is a list of json strings representing the commands to execute
        and nActions is the number of actions/commands in the list """
    def setReflex(self,name,conditions,actions,nActions):
        s = toJson("setReflex",name,0.0,0.0,0.0,[conditions],1,actions,nActions)
        send(s,self.clientsocket)

    """ returns a json string containing the names of the current states
        or None if no data could be retrieved in the time specified by sleepPause """
    def getStates(self):
        s = toJson("getStates","",0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            r = getMessages(self.clientsocket)
            for msg in r:
                if msg != "":
                    print msg
                    json_data = json.loads(msg)
                    if "type" in json_data:
                        if json_data["type"] == "activeStates":
                            return msg
            if not waitForData:
                break
        print "Error: Could not retrieve states from PAGI world"
        return None

    """ This sets a state in PAGI world called 'name' for 'duration' number of seconds
        Setting duration to -1 makes the state active indefinitely. """
    def setState(self,name,duration):
        s = toJson("setState",name,duration,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

    """ This function loads a task in the PAGI World, where 'name' is the filepath of the
        task (PAGI looks in the same directory as the executable if running from executable file,
        otherwise it looks in the 'source' folder of the Unity project.) """
    def loadTask(self,name):
        s = toJson("loadTask",name,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

    #def saveTask(self,name):
    #    s = toJson("saveTask",name,0.0,0.0,0.0,[],0,[],0)
    #    send(s,self.clientsocket)

    """ This function prints text to the console of PAGI World """
    def printToConsole(self,text):
        s = toJson("print",text,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

    """ This function makes a speech bubble in the PAGI world
        The text to be said is contained in parameter text, where duration is the
        number of seconds for the message to be displayed, xpos/ypos are the coordinates
        of where to display the bubble, and speaker contains a character 'P' if the PAGI
        guy is saying the message, or 'N' if it is a general message said by no one. """
    def say(self,text,duration,xpos,ypos,speaker):
        # speaker is 'P' for pagi guy, or 'N' for no one
        s = toJson("say",text,duration,xpos,ypos,[speaker],1,[],0)
        send(s,self.clientsocket)

    """ This fuction sends a force to the PAGI guys hand.
        It takes parameters: hand as 'left' or 'right' and x as force in the horizontal direction
        and y as force in the vertical direction """
    def moveHand(self,hand,x,y):
        if hand.upper() == 'RIGHT':
            s = toJson("addForce", 'RHvec', 0.0, str(x), str(y), [], 0, [], 0)
            send(s, self.clientsocket)
        else:
            s = toJson("addForce", 'LHvec', 0.0, str(x), str(y), [], 0, [], 0)
            send(s, self.clientsocket)

    """ this returns a json string containing the information about a specified tactile sensor
        or returns None if the data could not be retrieved """
    def getTactileSensor(self,code):
        if code[0] != "B" and code[0]!= "R" and code[0] != "L":
            print "Error: invalid tactile sensor code specified"
            return None
        elif code[0] == "B" and (int(code[1]) > 7 or int(code[1]) < 0 ):
            print "Error: invalid range for body tactile sensor (should be 0-7)"
            return None
        elif code[0] != "B" and (int(code[1]) < 0 or int(code[1]) > 4):
            print "Error: invalid range for hand tactile sensor (should be 0-4"
            return None
        s = toJson("sensorRequest",code,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            r = getMessages(self.clientsocket)
            for msg in r:
                if msg != "":
                    print msg
                    json_data = json.loads(msg)
                    if "sensorCode" in json_data:
                        if json_data["sensorCode"] == code:
                            return msg
            if not waitForData:
                break
            print "Error: Could not retrieve states from PAGI world"
            return None

    """ returns a tuple containing the x and y values of the PAGI guy's position
        or None if it could not be retrieved """
    def getBodyPosition(self):
        s = toJson("sensorRequest","BP",0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            msg = getMessages(self.clientsocket)
            for i in msg:
                if i != "":
                    print i
                    json_msg = json.loads(i)
                    if "type" in json_msg:
                        if json_msg["type"] == "BP":
                            x = json_msg["x"]
                            y = json_msg["y"]
                            return x, y
            if not waitForData:
                break
        print "Error: could not retrieve body position data"
        return None

    """ This simple function returns the position of the PAGI guy's hand relative to his body
        it returns a tuple containing the x,y values on success or None if no data was retrieved"""
    def getHandPosition(self,hand):
        if hand.upper() == "RIGHT":
            code = "RP"
            s = toJson("sensorRequest","RP",0.0,0.0,0.0,[],0,[],0)
        else:
            code = "LP"
            s = toJson("sensorRequest","LP",0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            msg = getMessages(self.clientsocket)
            for i in msg:
                if i != "":
                    print i
                    json_msg = json.loads(i)
                    if "type" in json_msg:
                        if json_msg["type"] == code:
                            x = json_msg["x"]
                            y = json_msg["y"]
                            return x, y
            if not waitForData:
                break
        print "Error: could not retrieve hand position data"
        return None


    """ This gets data from a vision sensor
        parameter code contains 'P' for peripheral sensor or 'D' for detailed sensor
        x and y are the coordinates of the sensor in the sensor map (0,0 to 30,20 for Detailed
        and 0,0 to 15,10 for peripheral vision)
        this returns a json string containing all data returned by the sensor """
    def getVisionSensor(self,code,x,y):
        if code != 'V' and code != 'P':
            print "Error: invalid vision sensor code specified, must be 'V' or 'P'"
            return None
        elif code == 'V' and (x > 30 or x < 0 or y < 0 or y > 20):
            print "Error: invalid vision sensor code range."
            return None
        elif code == 'P' and (x > 15 or x < 0 or y > 10 or y < 0) :
            print "Error: invalid vision sensor code range."
            return None

        code = code + str(x) + '.' + str(y)
        s = toJson("sensorRequest",code,0.0,0.0,0.0,[],0,[],0)
        send(s,self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            msg = getMessages(self.clientsocket)
            for i in msg:
                if i != "":
                    print i
                    json_msg = json.loads(i)
                    if "sensorCode" in json_msg:
                        if json_msg["sensorCode"] == code:
                            return i
            if not waitForData:
                break

        print "Error: no sensor data could be retrieved from sensor " + code
        return None

    """ this returns a json string containing all sensor map data retrieved from unity
        Note that this function would perform better if waitForData is set to false, and
        a custom function for receiving messages takes care of the data when it arrives. """
    def getSensorMap(self,code):
        if code == "MDN":
            s = toJson("sensorRequest","MDN",0.0,0.0,0.0,[],0,[],0)
        elif code == "MPN":
            s = toJson("sensorRequest","MPN",0.0,0.0,0.0,[],0,[],0)
        else:
            print "Error: Invalid map sensor code."
            return None

        send(s, self.clientsocket)

        if not waitForData:
            time.sleep(sleepPause)

        while 1:
            msg = getMessages(self.clientsocket)
            for i in msg:
                if i != "":
                    print i
                    json_msg = json.loads(i)
                    if "type" in json_msg:
                        if json_msg["type"] == code:
                            return i
            if not waitForData:
                break

        print "Error: No sensor map data retreived"
        return None

    """This allows for a force to be sent to an effector using an expression instead of a single value
        It assumes ef is a valid effector code, and that the expression is formatted as described in the documentation
        expx is the expression used for force in the horizontal direction
        expy is the expression used for force in the vertical direction"""
    def addForceExpression(self,ef,expx,expy):
        if expx == "":
            expx = "[0]"
        if expy == "":
            expy = "[0]"
        s = toJson("addForce", ef, 0.0, 0.0, 0.0, [expx,expy], 2, [], 0)
        send(s, self.clientsocket)
