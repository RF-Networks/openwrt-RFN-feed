#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=Bermad-Gateway
PKG_VERSION:=2.0.4
PKG_RELEASE=1

PKG_SOURCE_URL:=https://bitbucket.org/rfnetwork/bermadgateway.git
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=cca94621d8c346c3f4469a6e4480c9c43707fd74
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)
  CATEGORY:=Bermad
  TITLE:=Bermad-Gateway software
  DEPENDS:=+libstdcpp +zlib +boost-filesystem +RFGSMlib +libserial +libopenssl +libubox +libuci +libgpiod 
endef

define Package/$(PKG_NAME)/description
  Bermad-Gateway software for reading tags.
endef

TARGET_CFLAGS+=-I$(STAGING_DIR)/usr/include
TARGET_LDFLAGS+=-L$(STAGING_DIR)/usr/lib

define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/usr/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/BermadGateway $(1)/usr/sbin/BermadGateway
	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
