"""
The 3 laws of Robotics

1 A robot may not injure a human being or, through inaction, allow a human being to come to harm.
2 A robot must obey the orders given to it by human beings, except where such orders would conflict with the First Law.
3 A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.

All messages comming in to the brain is through
    def addMessage(self,keyword):


First the current context must be esablished

1. get the current context

2. send the message to the function associated with the current context
    {NO_COMMUNICATION_HANDSHAKE,WAIT_FOR_COMMAND,ANY_OTHER_CONTEXT}

3. reply the response from the context handler

* NO_COMMUNICATION_HANDSHAKE
    look for naming
    
* WAIT_FOR_COMMAND
    a command can be a keyword or a system comman

    1. Look for system command
    2. Look for keyword
    3. Look for regexp match

* ANY_OTHER_CONTEXT
"""

import time
import csv
import sys
from time import gmtime, strftime, localtime

class AddDeviceHandler:

    pw = None
    user = None

    @classmethod
    def newMessage(self,message,init = False):

        if init == True:

            self.pw = None
            self.user = None

            return ("ADDING_DEVICE","Please give me your username")

        else:

            if self.user == None:

                self.user = message

                return ("ADDING_DEVICE","Please give me your password")

            else:

                self.pw = message

                #print "User %s Password %s" % (self.user,self.pw)

                # verify username and password

                # fetch all valid usernames and passwords

                users = ValidUsers("users.csv")

                if users.isValid(self.user,self.pw):
                    
                    return ("ADDING_DEVICE","Enter your keyword")

                else:

                    # if not valid give the username again
                    self.pw = None
                    self.user = None
                    
                    return ("NO_COMMUNICATION_HANDSHAKE","Wrong user or password. Must start again")

class ValidUsers:

    def __init__(self,filename):

        self.users = {}
        
        with open('users.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                #print row
                self.users[row[0]] = row[1]

    def addUser(self,username,pw):

        with open('users.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow((username,pw))

    def isValid(self,user,pw):

        if user in self.users:

            return (self.users[user] == pw)

        else:

            return False

        

class TheBrain:
   

    def __init__(self):

        self.context = None
        self.communicationHandshakeTimestamp = 0

        # for debug purposes
        self.lastResponse = ""
        self.lastMessage = ""

        
        self.systemCommands = {"add device" : "add device" , "new device" : "add device"}
        self.systemCommandHandlers = {"add device" : AddDeviceHandler.newMessage}
        

        self.contextHandler = {"NO_COMMUNICATION_HANDSHAKE" : self.makeHandshake
                               , "HAVE_COMMUNICATION_HANDSHAKE" : self.waitForCommand
                               , "ADDING_DEVICE" : AddDeviceHandler.newMessage}

        self.setDefaultContext()

    def makeHandshake(self,message):
        """
        Enter context NO_COMMUNICATION_HANDSHAKE
        Leaves context HAVE_COMMUNICATION_HANDSHAKE if the message is in valid pi names
        """

        if (message in ["pi","bi","pie"]):
            self.setHandshakeEstablished()
            return ("HAVE_COMMUNICATION_HANDSHAKE","hello master")
        else:
            return ("NO_COMMUNICATION_HANDSHAKE","Some noise")



    def waitForCommand(self,message):
        """
        Enter context HAVE_COMMUNICATION_HANDSHAKE

        Checks matches for

        a command can be a keyword or a system comman

        1. Look for system command
        2. Look for keyword
        3. Look for regexp match        
        """

        print "ENTERING WAIT FOR COMMAND"


        if message in self.systemCommands:

            return self.systemCommandHandlers[message](message, True)

        #return ("got a comman","i donno")
        return ("HAVE_COMMUNICATION_HANDSHAKE","i donno")

        

    def setDefaultContext(self):

        self.context = "NO_COMMUNICATION_HANDSHAKE"

    def setHandshakeEstablished(self):

        self.context = "HAVE_COMMUNICATION_HANDSHAKE"
        self.communicationHandshakeTimestamp = time.time()

    def addMessage(self,message):
        """        
        First the current context must be esablished

        1. get the current context

        2. send the message to the function associated with the current context
            {NO_COMMUNICATION_HANDSHAKE,WAIT_FOR_COMMAND,ANY_OTHER_CONTEXT}

        3. reply the response from the context handler
        """

        # save the message for debug printing of brain stats
        self.lastMessage = message

        # check for timeout to reset de context to default mode
        if (self.communicationHandshakeTimestamp + 10) <= time.time():
            self.setDefaultContext()


        # we have the current context in self.context. Send the message to the correct context handler
        (self.context,response) = self.contextHandler[self.context](message)

        self.lastResponse = response
        
        return response
        

    def __str__(self):

        ret_str = "********** THE BRAIN *************\nContext %s\nCommunication timestamp %s\nMessage %s\nResponse %s" % (self.context,self.communicationHandshakeTimestamp,self.lastMessage,self.lastResponse)

        return ret_str

if __name__ == "__main__":

    p = ValidUsers("users.csv")

    print p.isValid('robert','123')

    

    b = TheBrain()

    #AddDeviceHandler.newMessage('hello',init = True)

    print b

    b.addMessage("pi")

    print b


    b.addMessage("add device")

    print b

    b.addMessage("robert")

    print b

    b.addMessage("1234")

    print b


    

    
    """
    print b
    
    b.setHandshakeEstablished()

    print b

    b.setDefaultContext()

    print b

    b.addMessage("pi")

    print b

    b.addMessage("add device")

    print b

    """

    #b.loggData("Hello my friend")

    

    #print b.memory

    #print b.addMessage("pi")
    #exit
    #b.addKeyToIR("this is the latest name", 543)
    #print b.addMessage("this is the latest name")
    
    #print b.addMessage("write mode")
    #print b.addMessage("robert")
    #print b.addMessage("123")

    

    """
    b.addIRSignal("a ir signal hex112312311")
    b.addIRKeyword("hex signal")

    print b.currentAddedIRSignal
    """    
