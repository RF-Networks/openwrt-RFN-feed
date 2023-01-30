#!/bin/bash
service=bermadgatewayd
service_exec=BermadGateway

if pgrep $service_exec > /dev/null; then
    echo "$service is running!!!"
else
    /etc/init.d/$service start
fi
