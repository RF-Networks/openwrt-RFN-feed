include $(TOPDIR)/rules.mk

PKG_NAME:=rfn-ucode-webui
PKG_VERSION:=2.0
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/rfn-ucode-webui
  CATEGORY:=RFN
  DEPENDS:=+uhttpd +ucode +ucode-mod-uci +ucode-mod-ubus +uhttpd-mod-ucode
  TITLE:=RFN ucode Full REST Web UI
endef

define Build/Configure
	true
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	mkdir -p $(TOPDIR)/files/www/
	if [ -f "./files/www/index.html" ]; then \
		mv ./files/www/index.html $(TOPDIR)/files/www/index.html; \
	fi
	$(call Build/Prepare/Default)
endef

define Build/Compile
	true
endef

define Package/rfn-ucode-webui/install
	$(INSTALL_DIR) $(1)/www/rfn
	$(CP) ./files/www/* $(1)/www/
endef

$(eval $(call BuildPackage,rfn-ucode-webui))
