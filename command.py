import time
from connection import SerialConnection
class Command:
    commandString = ""
    def __init__(self, string, x=None,y=None):
        self.ser = SerialConnection(250000)
        # self.ser = SerialConnection(250000)
        self.commandString = string
        if x is not None:
            self.commandString += ' X' + str(x)
        if y is not None:
            self.commandString +=  ' Y' + str(y)   
        return
    def getCommandStr(self):
        return (str.encode(self.commandString + '\r\n'))
    def execute(self, delay=None):
        if delay is not None:
            time.sleep(delay)
        
        # print('Sending command ' + self.commandString)
        self.ser.send(str.encode(self.commandString + '\r\n'))
        
        while True:
            response = self.ser.read()
            proceed = 'ok' in response.decode('utf-8')
            
            # time.sleep(.01)
            # print(response.decode('utf-8'),proceed)
            if proceed == True:
                # print('OK')
                break
        