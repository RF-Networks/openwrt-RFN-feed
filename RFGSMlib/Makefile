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

PKG_SOURCE_URL:=https://sourceforge.net/projects/netlinksockets/files/release/1.0.0-pre-6/
PKG_SOURCE_PROTO:=svn
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=EAC4F4108B5B26902D1FFD0492FBBB21
PKG_SOURCE:=netLink_v1.0.0_pre_6.zip

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
