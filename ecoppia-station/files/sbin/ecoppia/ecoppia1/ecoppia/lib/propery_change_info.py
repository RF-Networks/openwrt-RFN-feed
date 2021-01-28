class PropertyType:
    RFConfig = "TelitConfiguration"
    StationType = "StationType"

class PropertyChangeInfo:
    def __init__(self, type, payload, desired):
        self.type = type
        self.payload = payload
        self.desired = desired
