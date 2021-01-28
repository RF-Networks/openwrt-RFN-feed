from exceptions import *
import threading
import socket
import time  as t

from ecoppia.globals import *
from configuration.config import *
from ecoppia.lib.package_info import *

SEND_TIMEOUT_SECONDS = 2
RECEIVE_TIMEOUT_SECONDS = 60

class TcpConnector:

    def __init__(self):
        self.handlers = {}
        self.server_socket = None
        self.send_lock = threading.Lock()
        self.transport_in_stop_event = threading.Event()

    def packRawPkg(self, pkgInfo):
        b = bytearray()
        b.append(0x0A)
        b.append(pkgInfo.type)
        tlen = struct.unpack("2B", struct.pack("H", len(pkgInfo.payload)))
        b.append(tlen[0])	
        b.append(tlen[1])
        b.append(0x0A)
        #b.extend(pkgInfo.payload)
        b+= pkgInfo.payload
        b.append(0x0A)
        return b

    def unPackRawPkg(self, bmsg):
        type = int(bmsg[1])
        payload = bmsg[5:len(bmsg) - 1]
        return PackageInfo(type, payload)

    def doSendPkg(self, pkgInfo):
        try:
            _,w,_ = select.select([], [self.server_socket], [], SEND_TIMEOUT_SECONDS)        
            if (len(w) > 0):
                pkg = self.packRawPkg(pkgInfo)  
                with self.send_lock:      
                    self.server_socket.send(str(pkg))
            else:
                raise Exception("TimeOut in doSendPkg")
        except Exception as e:
            app_log.exception("server connector, error in doSendPkg")  
            raise      
        except Exception:
            e = sys.exc_info()[0]              
            app_log.exception("server connector, error in doSendPkg")
            raise

    def doReceiveExact(self, size, buffer):
        msg = bytearray()
        if(size == 0):
            return msg

        while(True):
            r,_,_ = select.select([self.server_socket], [], [], RECEIVE_TIMEOUT_SECONDS)
            if (len(r) > 0) :
                #app_log.info('Before read {0} bytes: {1}'.format(len(buffer),
                #bytearrayToStr(buffer)))

                data = self.server_socket.recv(size - len(msg))
                if(len(data) == 0):
                    raise Exception('Error in doReceiveExact, Receive 0 Bytes')

                #temp = bytearray()
                #temp.extend(data)
                #app_log.info('{0} bytes read {1}'.format(len(data),
                #bytearrayToStr(temp)))

                msg.extend(data)
                buffer.extend(data)
                if(len(msg) == size):
                    return msg
                elif (len(msg) > size):
                    raise Exception("Error in doReceiveExact, read more bytes than required")
            else:
                raise Exception("TimeOut in doReceiveExact")

    def doReceivePkg(self):

        #app_log.info("doReceivePkg started..")
        msg = bytearray()
                       
        beforePayload = self.doReceiveExact(5, msg)       

        if(beforePayload[0] != 0x0A or beforePayload[4] != 0x0A):
            raise Exception('doReceivePkg Failed !')
 
        payloadlen = int(binascii.hexlify(beforePayload[2:4]), 16) 
        payload = self.doReceiveExact(payloadlen, msg)        

        afterPayload = self.doReceiveExact(1, msg)

        if(afterPayload[0] != 0x0A):
            raise Exception('doReceivePkg Failed !')
        

        pkgInfo = self.unPackRawPkg(msg)

        if(SmartStPkgType.SmartStPkgTypeInfo[pkgInfo.type][0] != SmartStPkgType.MasterToSmartStation):
            raise Exception('Invalid Package Direction Received !')
                
        #if pkgInfo.type != SmartStPkgType.PuttyToSmartSt:
        #    app_log.info("Package Received : "+str(pkgInfo))
        return pkgInfo

    def subscribe(self, handler): 
        handler.setServerContext(self)        
        for in_type in handler.server_in_types:            
            self.handlers[in_type] = handler
            app_log.info("in server connector subscription of " + SmartStPkgType.getName(in_type) + " is completed !") 


    def transport(self):
        tcp_log.info("transport started..")
        while (True):
            try:
                pkgInfo = self.doReceivePkg()

                handler = self.handlers.get(pkgInfo.type, None)
                if handler != None:
                    handler.addPkgToHandlingQueue(pkgInfo)          
                else:
                    tcp_log.fatal("in Server Connector Transport, No Handler For Packet Type " + str(pkgInfo.type) + " Found !")
            except Exception:
                tcp_log.exception("server connector, error in transport")
                self.transport_in_stop_event.set()
                break

    def doRun(self):  

        # errorMsg[0] - last , errorMsg[1] - previous
        errorMsg = ("","")

        while (True):        
        
            try:    
                  
                if(errorMsg[0] == ""):         
                    tcp_log.info("wait for server")     
                
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)           
                self.server_socket.connect((SERVER_IP, SERVER_PORT))                                              

                tcp_log.info("server (" + SERVER_IP + ":" + str(SERVER_PORT) + ") is connected !")

                # Hand Shake
                self.doSendPkg(PackageInfo(SmartStPkgType.HandShake, NAME + ";" + str(software_version)))
                pkgInfo = self.doReceivePkg()        
                if (pkgInfo.type != SmartStPkgType.HandShakeAck):
                    #app_log.info("server ("+SERVER_IP+":"+str(SERVER_PORT)+")
                    #Handshake failed !")
                    raise Exception("server (" + SERVER_IP + ":" + str(SERVER_PORT) + ") Handshake failed !")              
                                               
                                   
                # HERE START THE HANDLER INCLUDE A THREAD TO HANDLE THE
                # COMPLETE STREAM AGAINST THE MASTER
                tcp_log.info("server (" + SERVER_IP + ":" + str(SERVER_PORT) + ") Handshake completed successfully !")                  
                 
 
                self.transport_in_stop_event.clear()
                thread.start_new_thread(self.transport, ())

                # reset last error message
                errorMsg = ("","")

                # wait until the transport thread signal
                self.transport_in_stop_event.wait()

                tcp_log.error("something wrong happened in transport thread")
            except Exception as e:
                if (errorMsg[0] != str(e.args)):
                    tcp_log.exception("server connector, error")
                errorMsg = (str(e.args), errorMsg[0])
            except Exception:
                e = sys.exc_info()[0]
                if (errorMsg[0] != str(e)):
                    tcp_log.exception("server connector, error") 
                errorMsg = (str(e), errorMsg[0])     
            finally:
                #app_log.info("server connector, finally..  in doRun")
                try:
                    self.server_socket.shutdown(socket.SHUT_RDWR)
                except Exception:
                    if(errorMsg[0] != errorMsg[1] or errorMsg[0] == ""):
                        tcp_log.error("Exception in server_socket.shutdown(socket.SHUT_RDWR)")

                try:
                    self.server_socket.close()
                except Exception:
                    if(errorMsg[0] != errorMsg[1] or errorMsg[0] == ""):
                        tcp_log.error("Exception in server_socket.close()")	
                else:
                    if(errorMsg[0] != errorMsg[1] or errorMsg[0] == ""):
                        tcp_log.info("server socket closed successfully !")

                t.sleep(3)