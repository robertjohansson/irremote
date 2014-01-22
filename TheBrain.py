"""
The 3 laws of Robotics

A robot may not injure a human being or, through inaction, allow a human being to come to harm.
A robot must obey the orders given to it by human beings, except where such orders would conflict with the First Law.
A robot must protect its own existence as long as such protection does not conflict with the First or Second Law.
"""

import time
import csv
import sys
from time import gmtime, strftime, localtime

class TheBrain:
   

    def __init__(self):

        self.pw = "123"
        self.us = "robert"

        # inner states       
        self.communicationHandshake = False
        self.communicationHandshakeTimestamp = 0

        # used to add a new device
        self.waitingForAuthetification = False
        self.writemode = False
        
        self.currentUser = None
        self.currentPassword = None

        self.addDevice = ["write mode","add device"]
        
        self.piNames = ["pi","bi","pie"]
        self.addIRSignalKeywords = ["add device","new signal"]
        
        self.memory = self.getMemoryDic()

    def loggData(self,logMessage):

        with open('some.csv', 'a') as f:
            writer = csv.writer(f)
            writer.writerow((strftime("%Y-%m-%d %H:%M:%S", localtime()),logMessage))

    def lookupKeyword(self,keyword):

        if keyword in self.memory:

            return self.memory[keyword]

        else:

            return None

    def addIRKeyword(self,keyword):
        """
        Gets a new keyword for a device
        """
        
        

    def addIRSignal(self,irValue):
        """
        Gets a IR signal and stores it if we should do so
        """
        if self.addIRSignal:

            self.currentAddedIRSignal = irValue
        
    def saveMemoryDic(self):
        
        import pickle
        output = open('mem.pkl', 'wb')
        pickle.dump(self.memory,output)

    def addKeyToIR(self,keyword,ir):

        self.memory[keyword] = ir

        self.saveMemoryDic()

    def getMemoryDic(self):

        try:
            import pickle
            inputfile = open('mem.pkl', 'rb')
            memory = pickle.load(inputfile)
            return memory
        except:
            return {"enpty" : None}

    def addMessage(self,keyword):
        """
        keyword - a sentence spoken by the user

        A appropriate text response is being created
        """
        # if the communication handshake has timeout
        if (self.communicationHandshakeTimestamp + 10) <= time.time():
            self.communicationHandshake = False
            self.waitingForAuthetification = False
            self.writemode = False

            self.currentUser = None
            self.currentPassword = None
        

        # if communication handshake have been made
        if self.communicationHandshake:

            #if we are in writemode
            if self.writemode:

                pass

                

            else:

                # if we are waiting for username and password
                if self.waitingForAuthetification:

                    # check to see is we have stored a username
                    if self.currentUser == None:

                        self.currentUser = keyword
                    else:
                        self.currentPassword = keyword
                        
                        # check the username and password
                        if self.currentUser == self.us and self.currentPassword == self.pw:

                            # now we are in write mode

                            self.writemode = True
                            return "welcome to write mode enter a keyword"

                    

                    return "Enter your password"
                    
                else:

                    #if we want to add a device
                    if keyword in self.addDevice:

                        # do some authentification
                        self.waitingForAuthetification = True
                        self.communicationHandshakeTimestamp = time.time()

                        return "Enter your username"
                        
                    elif keyword in self.piNames:
                        
                        self.communicationHandshakeTimestamp = time.time()
                        return "Yes sir"         

                    # check to see if keyword being used exists in memory
                    elif keyword in self.memory:
                        #renew time step
                        self.communicationHandshakeTimestamp = time.time()

                        # make action upon keyword
                        #
                        #
                        #

                        
                        
                        # log the action done
                        #
                        #
                        #

                        logMessage = "Sucessfully done key %s val %s" % (str(keyword),str(self.memory[keyword]))

                        self.loggData(logMessage)
                        
                        return logMessage
                    else:
                        return "That keyword is not defined"

        # establish communication or regard input as noise
        else:

            if keyword in self.piNames:
                            
                self.communicationHandshake = True
                self.communicationHandshakeTimestamp = time.time()
                return "Yes sir"

            else:
                return "Noise recieved handshake not made"

if __name__ == "__main__":

    b = TheBrain()

    #b.loggData("Hello my friend")

    

    #print b.memory

    print b.addMessage("pi")
    #b.addKeyToIR("this is the latest name", 543)
    print b.addMessage("this is the latest name")
    
    #print b.addMessage("write mode")
    #print b.addMessage("robert")
    #print b.addMessage("123")

    

    """
    b.addIRSignal("a ir signal hex112312311")
    b.addIRKeyword("hex signal")

    print b.currentAddedIRSignal
    """    
