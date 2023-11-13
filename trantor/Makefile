include $(TOPDIR)/rules.mk

PKG_NAME:=libtrantor
PKG_VERSION:=1.5.14
PKG_RELEASE:=1

PKG_SOURCE_URL:=https://github.com/an-tao/trantor.git
PKG_SOURCE_PROTO:=git
PKG_SOURCE_SUBDIR:=$(PKG_NAME)-$(PKG_VERSION)
PKG_SOURCE_VERSION:=dd133c7bca937c652c76cb03c9e128fd76fb7bda

PKG_BUILD_DEPENDS:=c-ares openssl

PKG_BUILD_PARALLEL:=1

CMAKE_INSTALL:=1

include $(INCLUDE_DIR)/package.mk
include $(INCLUDE_DIR)/cmake.mk

define Package/$(PKG_NAME)
  SECTION:=rfn
  CATEGORY:=RFN
  TITLE:=TRANTOR
  DEPENDS:=+libstdcpp +libopenssl +libcares
endef

define Package/$(PKG_NAME)/description
  A non-blocking I/O cross-platform TCP network library, using C++14
endef

CMAKE_OPTIONS += -DBUILD_SHARED_LIBS:BOOL=ON \
									-DBUILD_DOC:BOOL=OFF \
									-DTRANTOR_USE_TLS=openssl \
									-DBUILD_C-ARES:BOOL=OFF \
									-DBUILD_TESTING:BOOL=OFF \
									-DUSE_SPDLOG:BOOL=OFF
		

define Package/InstallDev
	$(INSTALL_DIR) $(1)/usr/include
	$(CP) $(PKG_INSTALL_DIR)/usr/include/* $(1)/usr/include/
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/$(PKG_NAME).so $(1)/usr/lib/
endef
		
define Package/$(PKG_NAME)/install
	$(INSTALL_DIR) $(1)/usr/lib
	$(CP) $(PKG_INSTALL_DIR)/usr/lib/$(PKG_NAME).so* $(1)/usr/lib/
endef

TARGET_CFLAGS+=-I$(STAGING_DIR)/usr/include
TARGET_LDFLAGS+=-L$(STAGING_DIR)/usr/lib

$(eval $(call BuildPackage,$(PKG_NAME)))