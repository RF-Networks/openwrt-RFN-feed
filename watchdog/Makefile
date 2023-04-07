# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=RFN-Watchdog
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/RFN-Watchdog
  TITLE:=RFN Watchdog
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_mediatek_linkit-smart-7688 \
		+libpthread +libstdcpp +base-files

  CATEGORY:=RFN
  DEFAULT:=y
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
endef

define Build/Compile
        $(TARGET_CXX) $(TARGET_CXXFLAGS) -pthread -std=c++11 src/GPIO.cpp src/main.cpp -o $(PKG_BUILD_DIR)/rfnwatchdog
endef

define Package/RFN-Watchdog/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/rfnwatchdog $(1)/usr/bin/rfnwatchdog
	$(CP) ./files/* $(1)/
endef

$(eval $(call BuildPackage,RFN-Watchdog))
