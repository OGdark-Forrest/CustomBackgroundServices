import socket
import threading
from utils import general

logger = general.setLogger("SoundcoreAPI.py")

class Soundcore():
    def __init__(self, macaddress: str, onEvent = None):
        self.macaddress = macaddress
        self.Port = self.getPort()
        if self.Port is None:
            logger.debug("Port Not Found")
            return
        self.client = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.__thread = threading.Thread(target=self.__ParseReceiveData)
        self._running = True
        self.callback = onEvent 
        self.data = ""

    def __recvData(self):
        if not (data := self.client.recv(1024)) == self.data:
            self.data = data
            if self.callback != None:
                threading.Thread(target = self.callback, args=(self.data,)).start()

    def __ParseReceiveData(self):
        try:
            if self._running:
                self.__recvData()
                self.__ParseReceiveData()
        except Exception as e:
            if 'timed out' or "[WinError 10054]" in list(str(e)):
                print(e)
                return
            else:
                pass
                #print(e)

    def getPort(self):
        for x in range(1, 31):
            try:
                s = socket.socket(
                    socket.AF_BLUETOOTH,
                    socket.SOCK_STREAM,
                    socket.BTPROTO_RFCOMM
                )
                s.settimeout(2)
                s.connect((self.macaddress, x))
                s.close()
                return x
            except OSError:
                pass

        return None
    # def GetNearby_devices(self):
    #     #return bluetooth.discover_devices(lookup_names=True)
    #     return bluetooth.find_service(address=self.macaddress)
    
    def send(self, data):
        from time import sleep
        #print(data)
        self.client.send(bytearray.fromhex(data))
        sleep(0.1)


    def parseInfo(self):
        self.send("08ee00000001010a0002")

        for _ in range(50):
            if len(self.data) >= 68:
                break

            import time
            time.sleep(0.1)

        if len(self.data) < 68:
            print("Didn't receive enough data")
            return None

        return {
            "battery": self.data[9] * 10,
            "ANC": self.data[44:47],
            "SN": self.data[53:68],
            "firmware": self.data[48:52]
        }

    def ANC(self, modes: str):
        '''
        "Transparency": Set your headphone to Transparency mode
        "Normal": Set your headphone to Normal mode
        "ANC Indoor": Set your headphone to ANC Indoor mode
        "ANC Outdoor": Set your headphone to ANC Outdoor mode
        "ANC Transport": Set your headphone to ANC Transport mode
        '''
        base = "08ee00000006810e000"
        if modes == "Transparency":
            self.send(base+"10101008e")
        elif modes == "Normal":
            self.send(base+"20101008f")
        elif modes == "ANC Indoor":
            self.send(base+"00201008e")
        elif modes == "ANC Outdoor":
            self.send(base+"00101008d")
        elif modes == "ANC Transport":
            self.send(base+"00001008c")
        

    def connect(self):
        """
        This sets up the connection.
        """
        if self.Port:
            self.client.connect((self.macaddress, self.Port))
            self.__thread.start()
        else:
            return

    def close(self):
        """
        This stops the bluetooth connection with headphone, If you dont do this your Mobile app may not able to connect.
        """
        self._running = False
        self.client.close()
        self.__thread.join()
        print("Disconnected")