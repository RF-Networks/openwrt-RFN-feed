from executable_request import *

RESET_CONFIG_TIME_SEC = 2

class RfConfigurationRequest(ExecutableRequest):

    def __init__(self, name, commands, doResetBeforeConfig):
        ExecutableRequest.__init__(self)

        self.Name = name
        self.Commands = commands #RfConfigCommand
        self.DoResetBeforeConfig = doResetBeforeConfig

    def execute(self):

        telit_connector = self.telit_connector
        
        self.update_rf_configuration(self.Name)

        response = RfConfigUpdateResponse(self.Name, True)

        response.Name = self.Name
        
        rslt = telit_connector.StartConfigMode()
        if rslt != TelitResponseType.RFAckOk:
            response.Success = False

        if self.DoResetBeforeConfig:
            rslt = telit_connector.ResetConfiguration()
            if rslt != TelitResponseType.RFAckOk:
                response.Success = False
            time.sleep(RESET_CONFIG_TIME_SEC)

            #rslt2 = telit_connector.EndConfigMode()
            #time.sleep(RESET_CONFIG_TIME_SEC)
            #rslt1 = telit_connector.StartConfigMode()
            #if rslt1 != TelitResponseType.RFAckOk or rslt2 != TelitResponseType.RFAckOk or rslt3 != TelitResponseType.RFAckOk:
            #    response.Success = False

        for command in self.Commands:
            rslt = telit_connector.AtsCommnad(command.ATS, command.Value)
            if rslt != TelitResponseType.RFAckOk:
                response.Success = False
            response.add_to_commands(RfConfigResultCommand(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), command.ATS, command.Value))

        rslt = telit_connector.EndConfigMode()
        if rslt != TelitResponseType.RFAckOk:
            response.Success = False
        return response

class RfGetConfigurationRequest(ExecutableRequest):

    def __init__(self, name, commands, doResetBeforeConfig):
        ExecutableRequest.__init__(self)

        self.Name = name
        self.Commands = commands #RfConfigCommand
        self.DoResetBeforeConfig = doResetBeforeConfig

    def execute(self):

        telit_connector = self.telit_connector
        
        self.update_rf_configuration(self.Name)

        response = RfConfigUpdateResponse(self.Name, True)

        response.Name = self.Name

        for command in self.Commands:
            rslt = telit_connector.AtsCommnad(command.ATS, "")
            if rslt.find("=") == -1:
                response.Success = False
            response.add_to_commands(RfConfigResultCommand(time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime()), command.ATS, rslt.split("=")[1]))

        return response

class RfConfigCommand:

    def __init__(self, ats, value):

        self.ATS= ats
        self.Value = value

class RfConfigUpdateResponse:

    def __init__(self, name, success):
        self.StationMessageType = 0
        self.Name = name
        self.Success = success
        self.Commands = [] # RfConfigResultCommand
        self.Validation = {}
    
    def add_to_commands(self, command):
        self.Commands.append(command)

class RfConfigResultCommand:

    def __init__(self, timestamp, ats, value):
        self.Timestamp = timestamp
        self.ATS = ats
        self.Value = value