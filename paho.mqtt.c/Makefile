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

PKG_LICENSE:=MIT
PKG_LICENSE_FILES:=COPYING

CMAKE_INSTALL:=1

CMAKE_OPTIONS = -DPAHO_BUILD_STATIC=TRUE -DPAHO_WITH_SSL=TRUE -DPAHO_ENABLE_TESTING=FALSE -DPAHO_HIGH_PERFORMANCE=TRUE

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)/Default
  TITLE:=Eclipse Paho MQTT C Client Library
  URL:=http://eclipse.org/paho
endef

define Package/$(PKG_NAME)/Default/description
  Eclipse Paho MQTT C client library for memory-managed operating systems.
endef

define Package/lib$(PKG_NAME)
  $(call Package/$(PKG_NAME)/Default)
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS:=+libpthread +libopenssl
endef

define Package/lib$(PKG_NAME)/description
  $(call Package/$(PKG_NAME)/Default/description)
endef

define Package/$(PKG_NAME)-cli
  $(call Package/$(PKG_NAME)//Default)
  SECTION:=utils
  CATEGORY:=Utilities
  DEPENDS:=+lib$(PKG_NAME)
  TITLE+= (cli)
endef

define Package/$(PKG_NAME)-cli/description
  $(call Package/$(PKG_NAME)/Default/description)
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/MQTT*.h $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libpaho-mqtt3*.so* $(1)/usr/lib/	
endef

define Package/lib$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libpaho-mqtt3*.so* $(1)/usr/lib/
endef

define Package/$(PKG_NAME)-cli/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(CP) $(PKG_INSTALL_DIR)/usr/bin/* $(1)/usr/bin/	
endef

$(eval $(call BuildPackage,lib$(PKG_NAME)))
$(eval $(call BuildPackage,$(PKG_NAME)-cli))