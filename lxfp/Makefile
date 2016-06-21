# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=lxfp
PKG_RELEASE:=1

include $(INCLUDE_DIR)/package.mk

define Package/lxfp
  TITLE:=Telit lxfp tool
  DEPENDS:=@TARGET_ramips_mt7688_LinkIt7688 \
		+libpthread +libstdcpp

  CATEGORY:=RFN
  DEFAULT:=y
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
endef

define Build/Compile
        $(TARGET_CXX) $(TARGET_CXXFLAGS) -pthread -std=c++11 src/at.c src/log.c src/Bootloader.cpp src/Device.cpp src/DeviceFactory.cpp src/GeBootloader.cpp src/HeBootloader.cpp src/LE9x0Bootloader.cpp src/LeV2Bootloader.cpp src/Uploader.cpp src/UploaderFirstAckVariant.cpp src/V2SerialBootloader.cpp src/lxfp.cpp src/xE910V2UsbBootloader.cpp -o $(PKG_BUILD_DIR)/lxfp
endef

define Package/lxfp/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/lxfp $(1)/usr/bin/lxfp
endef

$(eval $(call BuildPackage,lxfp))
