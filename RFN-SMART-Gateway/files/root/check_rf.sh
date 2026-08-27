#!/bin/bash
service=rfnsmartgatewayd
service_exec=RFN-SMART-Gateway

if pgrep $service_exec > /dev/null; then
    echo "$service is running!!!"
else
    /etc/init.d/$service start
fi
