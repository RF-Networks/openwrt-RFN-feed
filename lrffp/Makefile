# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=RFN-lrffp
PKG_RELEASE:=1.00.04

include $(INCLUDE_DIR)/package.mk

define Package/RFN-lrffp
  TITLE:=RFN lrffp
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688 \
		+libpthread +libstdcpp

  CATEGORY:=RFN
  DEFAULT:=y
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
endef

define Build/Compile
        $(TARGET_CXX) $(TARGET_CXXFLAGS) -pthread -std=c++11 src/Device.cpp src/DeviceFactory.cpp src/Uploader.cpp src/log.cpp src/lrffp.cpp src/GPIO.cpp -o $(PKG_BUILD_DIR)/lrffp
endef

define Package/RFN-lrffp/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/lrffp $(1)/usr/bin/lrffp
endef

$(eval $(call BuildPackage,RFN-lrffp))
