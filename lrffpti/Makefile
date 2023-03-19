# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk
include $(INCLUDE_DIR)/kernel.mk

PKG_NAME:=RFN-lrffpti
PKG_RELEASE:=1.00.03

include $(INCLUDE_DIR)/package.mk

define Package/RFN-lrffpti
  TITLE:=RFN lrffpti
  DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_LinkIt7688 \
		+libpthread +libstdcpp +zlib +libserial

  CATEGORY:=RFN
  DEFAULT:=y
endef

define Package/RFN-lrffpti/description
  Flash Programmer for TI CC13XX devices.
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
endef

define Build/Compile
        $(TARGET_CXX) $(TARGET_CXXFLAGS) -pthread -std=c++11 src/Device.cpp src/RFNMeshDevice.cpp src/RFNStarDevice.cpp src/DeviceFactory.cpp src/Uploader.cpp src/log.cpp src/lrffpti.cpp src/GPIO.cpp -o $(PKG_BUILD_DIR)/lrffpti -lz -lserial
endef

define Package/RFN-lrffpti/install
	$(INSTALL_DIR) $(1)/usr/bin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/lrffpti $(1)/usr/bin/lrffpti
endef

$(eval $(call BuildPackage,RFN-lrffpti))
