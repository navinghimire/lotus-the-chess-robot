import serial
class SerialConnection:
    class __SerialConnection:
        def __init__(self, baudrate, port = None):
            self.port = port
            self.baudrate = baudrate
            self.ser = self.connect()
            self.isAvailable = False
        def __str__(self):
            return repr(self) + self.port + self.baudrate
        def connect(self):
            ser = None
            for i in range (0,10):
                try:
                    port = '/dev/ttyACM'+str(i)
                    print("Tyring to open port " + port + '...')
                    ser = serial.Serial(port, self.baudrate, timeout = 2)
                    if (ser.isOpen()):
                        print("Connection successful")
                        self.isAvailable = True
                        break

                except:
                    print(port + ' not available.')
            return ser
        def close(self):
            print("Connection closed")
            self.ser.close()
        def send(self,cmdStr):
            self.ser.write(cmdStr)
    instance = None
    def __init__(self,baudrate, port=None):
        if not SerialConnection.instance:
            SerialConnection.instance = SerialConnection.__SerialConnection(baudrate, port)
        else:
            SerialConnection.instance.port = port
            SerialConnection.instance.baudrate = baudrate
    def close(self):
        self.instance.close()
    def send(self,commandString):
        self.instance.send(commandString)
    def read(self):
        return self.instance.ser.readline()
    def __getattr__(self, name):
        return getattr(self.instance,name)

