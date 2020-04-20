#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=libnlsocketscpp
PKG_VERSION:=1.0.0
PKG_RELEASE=1

PKG_SOURCE_URL:=https://sourceforge.net/projects/netlinksockets/files/release/1.0.0-pre-6/
PKG_SOURCE_PROTO:=svn
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=EAC4F4108B5B26902D1FFD0492FBBB21
PKG_SOURCE:=netLink_v1.0.0_pre_6.zip

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=NetLink Sockets C++ Library
  DEPENDS:=+libstdcpp 
endef

define Package/$(PKG_NAME)/description
  Networking/Socket C++ Library.
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/$(PKG_NAME).so* $(1)/usr/lib/
endef

define Package/$(PKG_NAME)/install
    $(INSTALL_DIR) $(1)/usr/lib
endef

$(eval $(call BuildPackage,$(PKG_NAME)))