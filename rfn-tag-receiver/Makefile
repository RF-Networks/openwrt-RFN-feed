#
# Copyright (C) 2019 RF-Networks Ltd.
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=rfn-tag-receiver
PKG_VERSION:=2019-09-03
PKG_RELEASE=1.0.28

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
