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

PKG_SOURCE_URL:=https://bitbucket.org/rfnetwork/rfgsmlib/get
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=4234fe0df29025503e25087f175b42287b66de16
PKG_SOURCE:=$(PKG_NAME)-$(PKG_SOURCE_VERSION).tar.gz

PKG_BUILD_DIR:=$(BUILD_DIR)/$(PKG_NAME)-$(PKG_VERSION)

PKG_LICENSE:=LGPL-2.1+
PKG_LICENSE_FILES:=COPYING

SOURCES:=\
    $(PKG_BUILD_DIR)/gsmlib/gsm_at.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_cb.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_error.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_event.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_me_ta.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_nls.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_parser.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_phonebook.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sms.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sms_codec.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sms_store.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sorted_phonebook.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sorted_phonebook_base.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_sorted_sms_store.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_unix_serial.cc \
    $(PKG_BUILD_DIR)/gsmlib/gsm_util.cc 

TARGET_CXXFLAGS += -DHAVE_CONFIG_H $(FPIC) -I$(PKG_BUILD_DIR)
TARGET_LDFLAGS += -shared

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=GSM C++ libraries
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688 \
		+libstdcpp        
endef

define Package/$(PKG_NAME)/description
  A library to access GSM mobile phones via GSM modems.
endef

define Build/Compile
    $(TARGET_CXX) $(TARGET_CXXFLAGS) $(SOURCES) $(TARGET_LDFLAGS) -o $(PKG_BUILD_DIR)/$(PKG_NAME).so
endef

define Build/InstallDev
    $(INSTALL_DIR) $(PKG_INSTALL_DIR)/usr/include/gsmlib
	$(CP) \
            $(PKG_BUILD_DIR)/gsmlib/*.h \
            $(PKG_INSTALL_DIR)/usr/include/gsmlib/

	$(INSTALL_DIR) $(PKG_INSTALL_DIR)/usr/lib
	$(CP) \
		$(PKG_BUILD_DIR)/$(PKG_NAME).so* \
		$(PKG_INSTALL_DIR)/usr/lib/
endef

define Package/$(PKG_NAME)/install
    $(INSTALL_DIR) $(1)/usr/lib
	$(CP) \
		$(PKG_BUILD_DIR)/$(PKG_NAME).so* \
		$(1)/usr/lib/
endef

$(eval $(call BuildPackage,$(PKG_NAME)))
