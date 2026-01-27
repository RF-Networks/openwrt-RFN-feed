#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=libserial
PKG_VERSION:=1.0.0

PKG_RELEASE=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/crayzeewulf/libserial.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=461b19e2f883574b9d52b3eb94d25847ebfbd85a
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
CMAKE_INSTALL:=1

PKG_MAINTAINER:=Libserial Deveopment Team <crayzeewulf@gmai.com>
PKG_LICENSE:=LGPL-2.1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/libserial
  TITLE:=Serial port library
  SECTION:=libs
  CATEGORY:=Libraries
  DEPENDS:=+libstdcpp +boost +boost-system +boost-timer +boost-test +python
  DEFAULT:=y
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libserial* $(1)/usr/lib/
endef

define Package/libserial/install
    $(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libserial.so.* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,libserial))
