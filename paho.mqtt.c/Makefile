#
# Copyright (C) 2008-2012 OpenWrt.org
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=paho.mqtt.c
PKG_VERSION:=1.3.2
PKG_RELEASE:=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/eclipse/paho.mqtt.c.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=3148fe2d5f4b87e16266dfe559c0764e16ca0546
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
CMAKE_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)
  TITLE:=Eclipse Paho MQTT C Client Library
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS:=
endef

define Package/$(PKG_NAME)/description
  Eclipse Paho MQTT C client library for memory-managed operating systems.
endef

define Package/$(PKG_NAME)/install

endef

$(eval $(call BuildPackage,$(PKG_NAME)))
