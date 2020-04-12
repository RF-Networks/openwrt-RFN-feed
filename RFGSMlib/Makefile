#
# Copyright (C) 2007-2016 OpenWrt.org
# Copyright (C) 2020 RF-Networks Ltd. <info@rf-networks.com>
#
# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=RFGSMlib
PKG_VERSION:=2.0.0
PKG_RELEASE:=1

PKG_SOURCE_URL:=https://bitbucket.org/rfnetwork/rfgsmlib.git
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=4234fe0df29025503e25087f175b42287b66de16
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_INSTALL:=1

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING
PKG_MAINTAINER:=RF-Networks Ltd. <info@rf-networks.com>

include $(INCLUDE_DIR)/package.mk

define Package/RFGSMlib
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=GSM C++ libraries
  DEPENDS:=
endef

define Package/RFGSMlib/description
  A library to access GSM mobile phones via GSM modems.
endef

define Package/RFGSMlib/install
    $(INSTALL_DIR) $(1)/usr/lib

endef

define Build/InstallDev
    $(INSTALL_DIR) $(1)/usr/include/$(PKG_NAME)
    $(INSTALL_DIR) $(1)/usr/include

    $(INSTALL_DIR) $(1)/usr/lib
endef

$(eval $(call BuildPackage,RFGSMlib))
