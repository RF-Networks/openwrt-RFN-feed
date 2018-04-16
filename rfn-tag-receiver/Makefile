#
# Copyright (C) 2015 John Crispin <blogic@openwrt.org>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=rfn-tag-receiver
PKG_VERSION:=2018-04-16
PKG_RELEASE=1.0.24

include $(INCLUDE_DIR)/package.mk

define Package/rfn-tag-receiver
  TITLE:=RF-Networks Tag Receiver
  DEPENDS:=@TARGET_ramips_mt7688_LinkIt7688 \
        +boost-signals +libpthread +libstdcpp \
        +libmosquitto +libubox +libuci +zlib
  CATEGORY:=RFN
  DEFAULT:=m
endef

define Build/Configure
	true
endef

define Build/Compile
	true
endef

define Package/rfn-tag-receiver/install
	$(CP) ./files/* $(1)
endef

$(eval $(call BuildPackage,rfn-tag-receiver))
