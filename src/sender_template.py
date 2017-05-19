import os, sys
import struct
import socket

## Remote Error handler
class ClarisseNetError(Exception):
    def __init__(self, command, value):
        self.value = value
        self.command = command
    def __str__(self):
        return '%s\n%s' % (self.value, self.command)

    def get_error(self):
        return '%s\n%s' % (self.value, self.command)

## Remote connection handler. By default, it will try to connect to localhost on port 55000
class ClarisseNet:
    ## Internal class used as connection status enum
    class Status:
        Ok = 1
        Error = -1

    ## Internal class used as execution mode enum
    class Mode:
        Script = 0
        Statement = 1

    ## Default constructor. By default, tries to connect to localhost:55000
    def __init__(self, host = "localhost", port=55000):
        self.status = self.Status.Error
        self.connect(host, port)

    ## Connect to the command port of a Clarisse/CNODE host.
    # @param host The name or the IP address of the remote Clarisse host.
    # @param port The command port set on the remote Clarisse host.
    def connect(self, host, port):
        self.close()
        self.status = self.Status.Error
        try:
            self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._socket.connect((host, port))
        except:
            raise ValueError('Failed to connect to ' + host + ':' + str(port))
        self.status = self.Status.Ok

    ## Run the specifed python script on a Clarisse/CNODE host.
    # @param script A block of python code (as string) to execute on the remote Clarisse host.
    # @return The method doesn't return result.
    def run(self, script):
        # Execute a block of python code on the remote host
        self._send(script, self.Mode.Script)

    ## Evaluate the specifed python statemement on a Clarisse/CNODE host.
    # @param statement A block of python code (as string) to execute on the remote Clarisse host.
    # @return The result is returned as string.
    def evaluate(self, statement):
        # Evaluate the input statement on the remote host and return the result as string.
        return self._send(statement, self.Mode.Statement)

    ## Close the connection to the command port.
    def close(self):
        if (self.status == self.Status.Ok):
            self._socket.close()

    ## Make sure the connection is properly closed
    def __del__(self):
        self.close()

    ## internal method used to communicate with the remove command port
    def _send(self, command, mode):
        if (self.status != self.Status.Ok):
            raise RuntimeError('Not connected to Clarisse')
        ## send the command
        command_size = len(command) + 1
        command_size = struct.pack("<I", command_size)
        self._socket.send(command_size)
        packet = str(mode) + command
        self._socket.send(packet)
        ## receive result size
        result_size = self._socket.recv(4)
        result_size = struct.unpack("<I", result_size)[0]
        ## receive result
        must_recv = True
        result = ''
        remaining = result_size
        while (must_recv):
            result += self._socket.recv(remaining)
            remaining = result_size - len(result)
            if remaining == 0: must_recv = False

        if (result[0] == '0'):
            raise ClarisseNetError(result[1:], command)
        else:
            result = result[1:]
            if (result == ''):
                return None
            else:
                return result


if len(sys.argv) >= 4:
    host = sys.argv[1]
    port = sys.argv[2]
    script = sys.argv[3]

    if os.path.exists(script):
        with open(script, "r") as f:
            script = f.read()
    try:
        clarisse = ClarisseNet(host, int(port))
        try:
            clarisse.run(script)
        except:
            print "Error - Can't establish a connection with Clarisse. Please check the given PORT and HOST"

        print "Script successfully sent"
    except:
        print "Error - Can't connect to Clarisse command port. Check Port and Host in your settings"