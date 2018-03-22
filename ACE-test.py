""" ACE-test.py by Austin Erickson
    This file serves as a test of all commands/requests that can be sent to PAGI-World.
    NOTE that the IP will need to be changed to the appropriate IP that the PAGI-World
    server is running on.
    """
import time
import math
import random
from pagi_api import *

#if you leave it blank, it will try to find the IP itself. Otherwise, you can
#type in an IP manually:
cs = connectSocket(ip="192.168.1.5")

#you can also type a port if you're not using the default 42209:
#cs = connectSocket(ip="128.113.243.43", port=230)

#create an agent and bind it to the port you just opened
agent = Agent(cs)
turnNum = 0

""" generic check and print any messages from PAGI-World """
def checkMSG():
    # check any new messages that were sent
    responses = getMessages(cs)
    for r in responses:
        if r != "":
            print "Message received: " + r

# sleep duration is the amount of time to pause when polling sensors or otherwise waiting
# it is measured in seconds
sleepDuration = 0.0001

def checkVisionSensors():
    ''' VISION SENSORS '''
    sleepDuration = 0.0001

    agent.getSensorMap("MDN")
    agent.getSensorMap("MPN")
    #time.sleep(10)
    checkMSG()

    for x in range(31):
        for y in range(21):
            agent.getVisionSensor("V", x, y)

    for x in range(16):
        for y in range(11):
            agent.getVisionSensor("P", x, y)

def checkOtherSensors():
    ''' Sensor Testing '''
    agent.getVelocity()
    time.sleep(sleepDuration)
    checkMSG()

    agent.getBodyPosition()
    time.sleep(sleepDuration)
    checkMSG()

    agent.getHandPosition("RIGHT")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getHandPosition("LEFT")
    time.sleep(sleepDuration)
    checkMSG()

    ''' BODY TACTILE SENSORS '''
    agent.getTactileSensor("B0")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B1")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B2")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B3")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B4")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B5")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B6")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("B7")
    time.sleep(sleepDuration)
    checkMSG()

    ''' HAND TACTILE SENSORS '''
    agent.getTactileSensor("R0")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("R1")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("R2")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("R3")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("R4")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("L0")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("L1")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("L2")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("L3")
    time.sleep(sleepDuration)
    checkMSG()

    agent.getTactileSensor("L4")
    time.sleep(sleepDuration)
    checkMSG()

def loadHeroTask():
    ''' TASK TESTING '''
    agent.loadTask("hero.tsk")
    time.sleep(sleepDuration)
    checkMSG()

def checkCommands():
    sleepDuration = 0.5
    ''' COMMAND TESTING '''
    agent.printToConsole("starting exhaustive test of commands")
    time.sleep(sleepDuration)
    checkMSG()

    agent.createItem("Assets/cat.jpeg", 3.0, 0.0, 0.0, "cat", 1, 0.0, 0, 3)
    time.sleep(sleepDuration)
    checkMSG()

    agent.addForceToItem("cat", 200.0, 2000.0)
    time.sleep(sleepDuration)
    checkMSG()

    agent.getInfoAboutItem("cat")
    time.sleep(sleepDuration)
    checkMSG()

    agent.destroyItem("cat")
    time.sleep(sleepDuration)
    checkMSG()

    agent.dropItem("redDynamite", 0.0, 0.0, "")
    time.sleep(sleepDuration)
    checkMSG()

    ''' STATE TESTING '''
    agent.getStates()
    time.sleep(sleepDuration)
    checkMSG()

    agent.setState("testingState", -1)
    time.sleep(sleepDuration)
    checkMSG()

    agent.getStates()
    time.sleep(sleepDuration)
    checkMSG()

    ''' REFLEX TESTING '''
    agent.getReflexes()
    time.sleep(sleepDuration)
    checkMSG()

    action1 = toJson("say", "The reflex fired, so says I", 10.0, 0.0, 0.0, ["P"], 1, [], 0)
    action2 = toJson("addForce", 'J', 0.0, 30.0, 0.0, "", 0, "", 0)
    actionString = [action1, action2]
    agent.setReflex("testReflex", "reflexState", actionString, 2)
    time.sleep(sleepDuration)
    checkMSG()

    agent.getReflexes()
    time.sleep(sleepDuration)
    checkMSG()

    agent.setState("reflexState", 100.0)
    time.sleep(sleepDuration)
    checkMSG()

    agent.getStates()
    time.sleep(sleepDuration)
    checkMSG()

    agent.removeReflex("testReflex")
    time.sleep(sleepDuration)
    checkMSG()


def performDance():
    sleepDuration = 0.50
    ''' Do a little dance to show off the movements '''
    for i in range(3):
        ''' MOVEMENT TESTING '''
        agent.rotate(30)
        time.sleep(sleepDuration)
        agent.rotate(0)
        time.sleep(sleepDuration)
        agent.rotate(330)
        time.sleep(sleepDuration)
        agent.rotate(0)
        time.sleep(sleepDuration)

        agent.moveHand('right', 2000.0, 0.0)
        time.sleep(sleepDuration)
        agent.moveHand('left', -2000.0, 0.0)
        time.sleep(sleepDuration)
        agent.moveHand('right', 0.0, 2000.0)
        time.sleep(sleepDuration)
        agent.moveHand('left', 0.0, 2000.0)
        time.sleep(sleepDuration)

        agent.moveH(1, 'right')
        time.sleep(sleepDuration)
        agent.moveH(1, 'left')
        time.sleep(sleepDuration)
        agent.moveH(1, 'left')
        time.sleep(sleepDuration)
        agent.moveH(1, 'right')
        time.sleep(sleepDuration)

        agent.addForceExpression("BMvec", "[0]", "[(BPy+1)*50000]")
        time.sleep(1)

performDance()
loadHeroTask()
checkVisionSensors()
checkOtherSensors()
checkCommands()

''' Say we are finished '''
agent.say("Wow, that was exhausting",3.0,0.0,0.0,"N")
checkMSG()

while 1:
   checkMSG()

closeClient(cs)

exit()