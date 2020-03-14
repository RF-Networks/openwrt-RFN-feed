#
# Copyright (C) 2015 John Crispin <blogic@openwrt.org>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=rfn-mtk-linkit-webui
PKG_VERSION:=2016-12-25
PKG_RELEASE=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://github.com/RF-Networks/RFN-linkit-smart-7688-webUI.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=fa50b7cb6b337452eb5e8040f01b3fc9cba9f373
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz

include $(INCLUDE_DIR)/package.mk

define Package/rfn-mtk-linkit-webui
  TITLE:=LinkIt Smart 7688 Webui
  DEPENDS:=@TARGET_ramips_mt7688_LinkIt7688 
  CATEGORY:=RFN
  HIDDEN:=1
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
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/zh-*.html $(1)/www/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/ru-*.html $(1)/www/
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/app/index.html $(1)/www/index_7688.html
	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,rfn-mtk-linkit-webui))
