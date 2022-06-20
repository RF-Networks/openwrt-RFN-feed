#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=ecoppia-station
PKG_VERSION:=0.40.0
PKG_RELEASE=2

#PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  CATEGORY:=Ecoppia
  TITLE:=Ecoppia Station software
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688 +python +python-pyserial +python-pip +libmraa +libmraa-python
endef

define Package/$(PKG_NAME)/description
  Ecoppia Station software for robots communication.
endef

define Build/Configure
  true
endef

define Build/Compile
  true
endef

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/sbin/ecoppia
	$(INSTALL_DIR) $(1)/sbin/ecoppia/ecoppia_logs
	$(INSTALL_DIR) $(1)/usb/bin
	$(INSTALL_DIR) $(1)/etc/uci-defaults
	$(CP) ./files/* $(1)
endef

define Package/$(PKG_NAME)/postinst
    #!/bin/sh
    # Check if we are on real system
    if [ -z "$${IPKG_INSTROOT}" ]; then
        (. /etc/uci-defaults/99_add_ecoppia_to_crontab)
        rm -f /etc/uci-defaults/99_add_ecoppia_to_crontab
        (. /etc/uci-defaults/99_set_root_password)
        rm -f /etc/uci-defaults/99_set_root_password
        (. /etc/uci-defaults/99_setup_network_interfaces)
        rm -f /etc/uci-defaults/99_setup_network_interfaces
    fi
    exit 0
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
