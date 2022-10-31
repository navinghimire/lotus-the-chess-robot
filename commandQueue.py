from collections import deque
from command import Command

class CommandQueue:
    cmd_home = Command('G28 X Y')
    cmd_pickup = Command('M280 P0 S70')
    cmd_dropoff = Command('M280 P0 S0')
    cmd_wait = Command('M400')
    cmd_gopos = Command('G1',20,20)
    commands = deque([])
    def __init__(self):
        return
    def push(self, command):
        self.commands.append(command)
    def executeAll(self, interval=None):
        while self.commands:
            if interval is not None:
                self.commands.popleft().execute(interval)
            else:
                self.commands.popleft().execute()
          
    