#
# Copyright (C) 2008-2012 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=paho.mqtt.cpp
PKG_VERSION:=1.1
PKG_RELEASE:=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/eclipse/paho.mqtt.cpp.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=f3a2a52259b5463ab50eee6d1c033cba18d6e84b
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
CMAKE_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/lib$(PKG_NAME)
  TITLE:=Eclipse Paho MQTT C++ Client Library
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS:=+libstdcpp +libpaho.mqtt.c
endef

define Package/lib$(PKG_NAME)/description
  Eclipse Paho MQTT C++ client library for memory-managed operating systems.
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include/mqtt
	$(CP) $(PKG_INSTALL_DIR)/usr/include/mqtt/*.h $(1)/usr/include/mqtt
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libpaho-mqttpp3*.so* $(1)/usr/lib/	
endef

define Package/lib$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libpaho-mqttpp3*.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,lib$(PKG_NAME)))
