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

@copyright Robert Johansson
            Byazit

Version 0.2
"""

import time
import csv
import sys
from time import gmtime, strftime, localtime

class IrSignalHandler:

    @classmethod
    def newKeyword(self,keyword,ircode):

        
        # add some code to trigger the actual ir signal

        # logg the event

        logMessage = "sending IR signal"

        with open('logg.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow((strftime("%Y-%m-%d %H:%M:%S", localtime()),logMessage))

        # return to NO_COMMUNICATION_HANDSHAKE context using no message feedback

        return ("NO_COMMUNICATION_HANDSHAKE","IR signal has been sent")

        

        

class AddDeviceKeywordHandler:
    """
    newMessage handler

    Context: ADDING_DEVICE_KEYWORD
        Handler for adding device keyword. Makes sure the same keyword is given twice

    Leave using context:

        ADDING_DEVICE_KEYWORD - after one keyword has been added
        ADDING_DEVICE_KEYWORD - after two none similar keywords have been added
        
        ADDING_DEVICE_IR - after two keywords have been given successfully


    ir handler

    Context: ADDING_DEVICE_IR
        Handler for storing the Keyword and ir

    Leave using context:

        NO_COMMUNICATION_HANDSHAKE - when new keyword and ir is stored
        
    """

    tmpKeyword = None

    @classmethod
    def newMessage(self,message,init = False):

        if self.tmpKeyword == None:

            self.tmpKeyword = message

            return ("ADDING_DEVICE_KEYWORD","You said - " + message +" - Please repeat it")

        else:

            # verify that the same keyword have been given

            if self.tmpKeyword == message:

                return ("ADDING_DEVICE_IR","keyword has been verifyed. Please give me IR")

            else:

                self.tmpKeyword = None

                return("ADDING_DEVICE_KEYWORD","The keyword are not the same. Choonse a keyword again")

    @classmethod
    def newIR(self,ir):

        print "''''''''''''''''''Adding ir to file''''''''''''''''''"

        keyword = self.tmpKeyword

        i = IRandKeyword('irandkey.csv')
        i.addIr(keyword,ir)

        print "\tadding keyword and ir to file"
        
        self.tmpKeyword = None
        
        return("NO_COMMUNICATION_HANDSHAKE","New device have been adden using keyword ")

class AddDeviceVerifyUserHandler:
    """
    Context: ADDING_DEVICE_VERIFY_USER
        Handler for checking user name and password

    Leave using context:

        ADDING_DEVICE_VERIFY_USER - after the username have been given
        ADDING_DEVICE_KEYWORD - after user and password have been verifyed
        NO_COMMUNICATION_HANDSHAKE - when communication is established
        
    """

    pw = None
    user = None

    @classmethod
    def newMessage(self,message,init = False):

        if init == True:

            self.pw = None
            self.user = None

            return ("ADDING_DEVICE_VERIFY_USER","Please give me your username")

        else:

            if self.user == None:

                self.user = message

                return ("ADDING_DEVICE_VERIFY_USER","Please give me your password")

            else:

                self.pw = message

                #print "User %s Password %s" % (self.user,self.pw)

                # verify username and password

                # fetch all valid usernames and passwords

                users = ValidUsers("users.csv")

                if users.isValid(self.user,self.pw):
                    
                    return ("ADDING_DEVICE_KEYWORD","Enter your keyword")

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

            import hashlib
            m = hashlib.md5()
            m.update(pw)
            writer.writerow((username,m.hexdigest()))

    def isValid(self,user,pw):

        if user in self.users:

            import hashlib
            m = hashlib.md5()
            m.update(pw)

            return (self.users[user] == m.hexdigest())

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
        self.systemCommandHandlers = {"add device" : AddDeviceVerifyUserHandler.newMessage}

        self.irHandler = IrSignalHandler.newKeyword
        
        self.irKeywords = {}
        self.loadKeywords()

        #self.keywords = {"green light" : IrSignalHandler.newKeyword}
        

        # context for messages
        self.contextMessageHandler = {"NO_COMMUNICATION_HANDSHAKE" : self.makeHandshake
                               , "HAVE_COMMUNICATION_HANDSHAKE" : self.waitForCommand
                               , "ADDING_DEVICE_VERIFY_USER" : AddDeviceVerifyUserHandler.newMessage
                               ,"ADDING_DEVICE_KEYWORD" : AddDeviceKeywordHandler.newMessage}

        # context for ir signals
        self.contextIrHandler = {"ADDING_DEVICE_IR" : AddDeviceKeywordHandler.newIR}

        
        self.setDefaultContext()

    def irSignal(self,irValue):

        # check to see if the current context will recieve ir signals

        self.lastMessage = "ir code [%s]" % irValue
        self.lastResponse = ""
        
        if self.context in self.contextIrHandler:

            (self.context,self.lastResponse) = self.contextIrHandler["ADDING_DEVICE_IR"](irValue)

        else:

            self.lastResponse = "Ignoring IR signal since context [%s] have no ir-handler" % self.context

        
        # we have the current context in self.context. Send the message to the correct context handler
        #(self.context,response) = self.contextIrHandler[self.context](irValue)

        return self.lastResponse

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

        # match to system commands

        if message in self.systemCommands:

            self.resetHandshakeTimeout()

            return self.systemCommandHandlers[message](message, True)

        # match to keywords
        
        if message in self.irKeywords:

            self.resetHandshakeTimeout()

            return self.irHandler(message,self.irKeywords[message])
                        
        return ("HAVE_COMMUNICATION_HANDSHAKE","i have no keyword matching [%s]" % message)

        

    def setDefaultContext(self):

        self.context = "NO_COMMUNICATION_HANDSHAKE"

    def resetHandshakeTimeout(self):

        self.communicationHandshakeTimestamp = time.time()

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
            self.resetHandshakeTimeout()

        # check for reestablishing or resetting handshake
        # this will enable users to jump back directly to default mode from any context

        if message in ["pi","bi","pie"]:
            (self.context,response) = self.contextMessageHandler["NO_COMMUNICATION_HANDSHAKE"](message)

            self.lastResponse = response

            return response

        ## TODO!!! Enable user to reset back to NO_COMMUNICATION_HANDSHAKE
        

        # lets see if there is a message handler for this specific context
        elif self.context in self.contextMessageHandler:

            # we have the current context in self.context. Send the message to the correct context handler
            (self.context,response) = self.contextMessageHandler[self.context](message)            

            self.lastResponse = response

            # reset the timeout. Give the user another 10 seconds behore handshake breaks
            self.resetHandshakeTimeout()
        
            return response

        # since there is no message handler for this context simply ignore it
        else:

            response = "Ignoring this since [%s] have no message handler" % self.context

            self.lastResponse = response

            return response

    def addUser(self,username,pw):

        us = ValidUsers("users.csv")
        us.addUser(username,pw)

    def getUsers(self):

        us = ValidUsers("users.csv")
        return us.users

    def loadKeywords(self):

        i = IRandKeyword("irandkey.csv")
        self.irKeywords = i.keywords

    def getKeywords(self):

        return self.irKeywords
        

    def __str__(self):

        ret_str = "********** THE BRAIN *************\nContext %s\nCommunication timestamp %s\nMessage %s\nResponse %s\n*********************************" % (self.context,self.communicationHandshakeTimestamp,self.lastMessage,self.lastResponse)

        return ret_str

class IRandKeyword:

    def __init__(self,filename):

        self.keywords = {}
        
        with open('irandkey.csv', 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                #print row
                self.keywords[row[0]] = row[1]

    def addIr(self,keyword,ir):

        with open('irandkey.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow((keyword,ir))

    def isValid(self,keyword):

        return keyword in self.keywords

    def getIR(self,keyword):

        return self.keywords[keyword]

"""
        CODE FOR TESTING
"""


def testIR():

    i = IRandKeyword('irandkey.csv')
    i.addIr("green light","hello world")
    print i.isValid("green light")
    print i.getIR("green light")

def testUsers():

    p = ValidUsers("users.csv")
    print p.isValid('robert','123')

def runBrainInTextMode():

    b = TheBrain()

    i = None

    print "================== Wellome to the brain =================="    
    print "i:ir code - to enter ir code"
    print "b:adduser - adds a user"
    
    print "b:status - to print status"
    print "b:users - to print all users"
    print "b:keywords - to print all users"
    print
    print "exit - to terminate"
    print "==========================================================="

    while i != "exit":

        
        i = raw_input()

        if i[0:2] == "i:":

            b.irSignal(i[2:])

        elif i == "b:status":

            print b

        elif i == "b:users":

            print b.getUsers()

        elif i == "b:adduser":

            print "user name"

            user = raw_input()

            print "password"

            pw = raw_input()

            b.addUser(user,pw)

        elif i == "b:keywords":

            print b.getKeywords()

        else:

            b.addMessage(i)

            print "%s\t%s" % (b.lastResponse,b.context)       
    
if __name__ == "__main__":

    

    runBrainInTextMode()

    
