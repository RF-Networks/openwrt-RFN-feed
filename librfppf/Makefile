#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=librfppf
PKG_VERSION:=4.0.2

PKG_RELEASE=$(PKG_SOURCE_VERSION)

PKG_SOURCE_PROTO:=git
PKG_SOURCE_URL:=https://x-token-auth:ATCTT3xFfGN0JjWIoGmEJi5pK36LaLWQzmc1kKdINwohR8dmYC9GSVT8Ly0T1Hw_Gkx40oy3gTCiYrJgCI78d0yP5tuP3H708S0hpkasCY8jVOjjFHFHt-Bw6TeFTzZ9iW_KvJ_-ogI59K4xRI-MVZ7fbejZAe-PDdCaAd-kIZKXnc2BPkOhdFg=540F27E4@bitbucket.org/rfnetwork/rfppf-c.git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=c2d95bff9100753908c57c95dac8bd506974fbd3
PKG_SOURCE:=$(PKG_NAME)-$(PKG_VERSION)-$(PKG_SOURCE_VERSION).tar.gz
CMAKE_INSTALL:=1

PKG_MAINTAINER:=Archil Pirmisashvili <archil@grf-networks.com>
PKG_LICENSE:=LGPL-2.1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

# Path to CMakeLists.txt
CMAKE_SOURCE_DIR:=$(PKG_BUILD_DIR)/RFPPFC++
# Force Shared Library build and disable examples to save space/time
CMAKE_OPTIONS += \
	-DBUILD_SHARED_LIBS=ON \
	-DCMAKE_POSITION_INDEPENDENT_CODE=ON \
	-DBUILD_EXAMPLES=OFF
	
define Package/librfppf
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=RF-Networks Parser Framework
  DEPENDS:=+libstdcpp
endef

# Override Configure to point to the subfolder
define Build/Configure
	$(call Build/Configure/Default,-S$(CMAKE_SOURCE_DIR))
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libRFPPFC++.so* $(1)/usr/lib/
endef

define Package/librfppf/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/libRFPPFC++.so* $(1)/usr/lib/
endef

$(eval $(call BuildPackage,librfppf))
