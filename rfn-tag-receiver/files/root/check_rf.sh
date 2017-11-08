#!/bin/bash
service=rftagreceiverd
service_exec=TagReceiver

if pgrep $service_exec > /dev/null; then
    echo "$service is running!!!"
else
    /etc/init.d/$service start
fi

