#
# Copyright (C) 2021 Archil Pirmisashvili <archil@rf-networks.com>
#

include $(TOPDIR)/rules.mk

PKG_NAME:=Sigmatec-Concentrator
PKG_VERSION:=2.0.12
PKG_RELEASE=1

PKG_SOURCE_URL:=https://bitbucket.org/rfnetwork/concentrator.git
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=433442306f8d8620274ce4b09cecc1d4c49426d6
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION).tar.gz

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)
	CATEGORY:=Sigmatec
	TITLE:=Sigmatec-Concentrator software
	DEPENDS:=+libstdcpp +zlib +boost-filesystem +boost-system +boost-date_time +libserial +libnlsocketscpp +libubox +libuci +libgpiod +libsqlite3 +smstools3
endef

define Package/$(PKG_NAME)/description
	Sigmatec Concentrator software for remote meter reading
endef

TARGET_CFLAGS+=-I$(STAGING_DIR)/usr/include
TARGET_LDFLAGS+=-L$(STAGING_DIR)/usr/lib

define Package/$(PKG_NAME)/install
			$(INSTALL_DIR) $(1)/usr/bin
			$(INSTALL_BIN) $(PKG_BUILD_DIR)/DisCon $(1)/usr/bin/DisCon
			$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
