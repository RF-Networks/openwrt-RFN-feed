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

PKG_MAINTAINER:=Libserial Deveopment Team <crayzeewulf@gmai.com>
PKG_LICENSE:=LGPL-2.1

PKG_INSTALL:=1
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/libserial
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=C++ library for serial port programming
  URL:=https://github.com/crayzeewulf/libserial
  DEPENDS:=+libstdcpp
endef

define Package/libserial/description
  LibSerial is a C++ library that provides a clean and easy-to-use 
  interface for accessing serial ports on POSIX systems.
endef

# Disable tests, docs, python and examples for embedded footprint
CMAKE_OPTIONS += \
	-DLIBSERIAL_ENABLE_TESTING=OFF \
	-DLIBSERIAL_ENABLE_EXAMPLES=OFF \
	-DLIBSERIAL_PYTHON_ENABLE=OFF \
	-DLIBSERIAL_ENABLE_DOCS=OFF \
	-DBUILD_TESTING=OFF \
	-DBUILD_DOCS=OFF \
	-DINSTALL_STATIC=ON \
	-DINSTALL_SHARED=ON

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
