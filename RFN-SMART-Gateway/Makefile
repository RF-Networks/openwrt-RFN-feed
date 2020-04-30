#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=RFN-SMART-Gateway
PKG_VERSION:=1.0.0
PKG_RELEASE=1

PKG_SOURCE_URL:=https://bitbucket.org/rfnetwork/rfn-smart-gateway.git
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=1a3af4fa8e788436613ad6308cca130c282e832e
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)
  CATEGORY:=RFN
  TITLE:=SMART-Gateway software
  DEPENDS:=+libstdcpp  +zlib +boost-filesystem +RFGSMlib +libserial +libnlsocketscpp +libmosquitto +libubox +libuci
endef

define Package/$(PKG_NAME)/description
  SMART-Gateway software for reading tags.
endef

TARGET_CFLAGS+=-I$(STAGING_DIR)/usr/include
TARGET_LDFLAGS+=-L$(STAGING_DIR)/usr/lib

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/RFN-SMART-Gateway $(1)/usr/bin/RFN-SMART-Gateway
	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,$(PKG_NAME)))