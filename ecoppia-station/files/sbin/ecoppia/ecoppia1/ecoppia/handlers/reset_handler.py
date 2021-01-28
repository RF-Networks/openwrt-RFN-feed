from ecoppia.globals import *
from ecoppia.lib.package_info import *

class ResetHandler:

    def __init__(self):
        self.server_in_types = [SmartStPkgType.HardReset]
        self.server_context = None

    def setServerContext(self, context):
        self.server_context = context

    def doBeforeHardReset(self, feasibility_rslt, sessionid, requestPkgInfo):
        ackPkg = PackageInfo(SmartStPkgType.HardResetAck, json.dumps({"Done": feasibility_rslt.possible, "Message": feasibility_rslt.description}) , sessionid)
        self.server_context.doSendPkg(requestPkgInfo, ackPkg)

    def processServerPackage(self, pkgInfo):
        self.server_context.reset_facilitator.DoHardReset(self.doBeforeHardReset, pkgInfo.sessionid, pkgInfo)



class MqttKeepaliveHandler:

    def __init__(self):
        self.server_in_types = [SmartStPkgType.MqttKeepAlive]
        self.server_context = None

    def setServerContext(self, context):
        self.server_context = context

    def processServerPackage(self, pkgInfo):
        self.server_context.doSendPkg(pkgInfo, PackageInfo(SmartStPkgType.MqttKeepAliveAck, "", pkgInfo.sessionid))


from ecoppia.lib.sqlite_facilitator import Dal
from ecoppia.lib.reset_facilitator import ResetFacilitator

class EnableWeather:

    def __init__(self, reset_facilitator):
        app_log.info("SubscriberByShadow")
        self.property_types = ["Weather"]
        self.reset_facilitator = reset_facilitator

    def setShadowContext(self, context):
        self.shadow_context = context

    def processPropertyChange(self, pkgInfo):
        try:
            isenable = str(pkgInfo.payload['Enable'])
            d = Dal()
            d.update_configuration('IsWeatherEnable', isenable)
            self.shadow_context.doReportState(pkgInfo.type, pkgInfo.desired)
            app_log.info("Rebooting the device due to \"IsWeatherEnable\" = " + isenable)
            self.reset_facilitator.DoApplicationReset()

        except Exception:
            weather_log.exception("shadow processPropertyChange failed")

class DisconnectedWatchdog:

    def __init__(self, mqtt_connector):
        app_log.info("SubscriberByShadow - DisconnectWatchdog")
        self.property_types = ["DisconnectedWatchdog"]
        self.mqtt_connector = mqtt_connector
        self._dal = Dal()

        try:
            disconnected_time_to_reset = float(self._dal.get_configuration('DisconnectedTimeToReset'))

            if not(disconnected_time_to_reset > MINIMAL_DISCONNECTED_TIME_TO_RESET):
                self.mqtt_connector.disconnected_time_to_reset = disconnected_time_to_reset
            else:
                self.mqtt_connector.disconnected_time_to_reset = MINIMAL_DISCONNECTED_TIME_TO_RESET
        except Exception as e:
            self.mqtt_connector.disconnected_time_to_reset = MINIMAL_DISCONNECTED_TIME_TO_RESET


    def setShadowContext(self, context):
        self.shadow_context = context

    def processPropertyChange(self, pkgInfo):
        try:
            disconnected_time_to_reset = pkgInfo.payload['DisconnectedTimeToReset']
            if disconnected_time_to_reset > MINIMAL_DISCONNECTED_TIME_TO_RESET:
                self.mqtt_connector.disconnected_time_to_reset = disconnected_time_to_reset
                self._dal.update_configuration('DisconnectedTimeToReset', disconnected_time_to_reset)
            else:
                self.mqtt_connector.disconnected_time_to_reset = MINIMAL_DISCONNECTED_TIME_TO_RESET

        except Exception:
            app_log.exception("shadow processPropertyChange failed")