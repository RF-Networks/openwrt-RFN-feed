#
# Copyright (C) 2015 John Crispin <blogic@openwrt.org>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=rfn-mtk-linkit-webui
PKG_VERSION:=2018-11-19
PKG_RELEASE=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/RF-Networks/RFN-linkit-smart-7688-webUI.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=ec65a415176ac8b8c08878fadf807d8e65e55a71
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz

include $(INCLUDE_DIR)/package.mk

define Package/rfn-mtk-linkit-webui
  TITLE:=LinkIt Smart 7688 Webui
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688
  CATEGORY:=RFN
  HIDDEN:=1
  DEFAULT:=y
endef

define Build/Configure
	true
endef

define Build/Compile
	true
endef

define Package/rfn-mtk-linkit-webui/install
	$(INSTALL_DIR) $(1)/www/build
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/build/* $(1)/www/build/
#	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/zh-*.html $(1)/www/
#	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/ru-*.html $(1)/www/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/index.html $(1)/www/index_7688.html
#	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,rfn-mtk-linkit-webui))
