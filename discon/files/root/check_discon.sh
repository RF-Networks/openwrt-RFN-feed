#!/bin/bash
service=discond
service_exec=DisCon

if pgrep $service_exec > /dev/null; then
    echo "$service is running!!!"
else
    /etc/init.d/$service start
fi

