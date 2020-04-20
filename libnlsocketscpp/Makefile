#
# Copyright (C) 2019 Archil Pirmisashvili <archil@rf-networks.com>
#
# This is free software, licensed under the GPL 2 license.
#

include $(TOPDIR)/rules.mk

PKG_NAME:=libnlsocketscpp
PKG_VERSION:=1.0.0
PKG_RELEASE=1

SOURCES:=\
    src/core.cc \
    src/smart_buffer.cc \
    src/socket.cc \
    src/socket_group.cc \
    src/util.cc \
	
TARGET_CXXFLAGS += $(FPIC) -I$(PKG_BUILD_DIR) -Isrc -pthread -Wcpp
TARGET_LDFLAGS += -lpthread -shared

include $(INCLUDE_DIR)/package.mk

define Package/$(PKG_NAME)
  SECTION:=libs
  CATEGORY:=Libraries
  TITLE:=NetLink Sockets C++ Library
  DEPENDS:=+libstdcpp 
endef

define Package/$(PKG_NAME)/description
  Networking/Socket C++ Library.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
endef

define Build/Compile
        $(TARGET_CXX) $(TARGET_CXXFLAGS) $(SOURCES) $(TARGET_LDFLAGS) -o $(PKG_BUILD_DIR)/$(PKG_NAME).so
		$(INSTALL_DIR) $(PKG_INSTALL_DIR)/usr/lib
		$(CP) $(PKG_BUILD_DIR)/$(PKG_NAME).so* $(PKG_INSTALL_DIR)/usr/lib/
		$(INSTALL_DIR) $(PKG_INSTALL_DIR)/usr/include/netlink
		$(CP) src/netlink/* $(PKG_INSTALL_DIR)/usr/include/netlink/
endef

define Build/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/$(PKG_NAME).so $(1)/usr/lib/
endef

define Package/$(PKG_NAME)/install
    $(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/$(PKG_NAME).so $(1)/usr/lib/
endef

$(eval $(call BuildPackage,$(PKG_NAME)))