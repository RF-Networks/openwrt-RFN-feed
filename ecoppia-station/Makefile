#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=ecoppia-station
PKG_VERSION:=0.0.1
PKG_RELEASE=1

#PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  CATEGORY:=Ecoppia
  TITLE:=Ecoppia Station software
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688 +python +python-pyserial +python-pip +libmraa +libmraa-python +libmraa-python3
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
	$(INSTALL_DIR) $(1)/sbin/ecoppia/certs
	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
