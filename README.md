# openwrt-RFN-feed
This feeds holds the software for RFN-SMART433 family units

# Build the firmware from sources

This section describes how to build the software for RFN-SMART433 family units from source codes.


### Host environment
The following operations are performed under a Ubuntu LTS 14.04.3 environment. For a Windows or a Mac OS X host computer, you can install a VM for having the same environment:
* Download Ubuntu 14.04.3 LTS image from [http://www.ubuntu.com](http://www.ubuntu.com)
* Install this image with VirtualBox (http://virtualbox.org) on the host machine. 50GB disk space reserved for the VM is recommanded


### Steps
In the Ubuntu system, open the *Terminal* application and type the following commands:

1. Install prerequisite packages for building the firmware:
    ```
    $ sudo apt-get install git g++ make libncurses5-dev subversion libssl-dev gawk libxml-parser-perl unzip wget python xz-utils
    ```

2. Download OpenWrt CC source codes:
    ```
    $ git clone https://github.com/RF-Networks/openwrt.git
	$ cd openwrt
	$ git checkout openwrt-19.07
    ```
    
3. Prepare the default configuration file for feeds:
    ```
    $ cp feeds.conf.default feeds.conf
    ```
    
4. Add the RFNWatchdog feed:
    
    ```
    $ echo src-git rfn https://github.com/RF-Networks/openwrt-RFN-feed.git;openwrt-19.07 >> feeds.conf
    ```
5. Update the feed information of all available packages for building the firmware:
    
    ```
    $ ./scripts/feeds update
    ```
6. Install all packages:
    
    ```
    $ ./scripts/feeds install -a
    ```
7. Start the compilation process:
    
    ```
    $ make V=99
    ```