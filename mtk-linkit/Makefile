# This is free software, licensed under the GNU General Public License v2.
# See /LICENSE for more information.

include $(TOPDIR)/rules.mk

PKG_NAME:=mtk-linkit
PKG_RELEASE:=1
PKG_BUILD_PARALLEL:=1

include $(INCLUDE_DIR)/package.mk

define Package/mtk-linkit
	TITLE:=MTK LinkIt Smart board support package
	DEPENDS:=@TARGET_ramips_mt76x8_DEVICE_mediatek_linkit-smart-7688 \
		+@KERNEL_DEVMEM +@BUSYBOX_DEFAULT_LSUSB +@BUSYBOX_DEFAULT_RUN_PARTS \
		+gdbserver +curl +strace +coreutils +coreutils-stty \
		+samba4-server +libmraa +openssh-sftp-server \
		+avahi-dbus-daemon +gpiod-tools +i2c-tools +blockd +block-mount \
		+uhttpd +uhttpd-mod-ubus +rpcd +rpcd-mod-iwinfo +rpcd-mod-file +nano \
		+luci +luci-theme-openwrt +luci-app-samba4 +luci-lib-json +luci-proto-qmi \
		+luci-proto-modemmanager +rpcd-mod-rpcsys +cgi-io +uboot-envtools \
		+kmod-cfg80211 +wireless-tools +libuci +serialconsole +kmod-usb-net +kmod-usb-net-qmi-wwan \
		+libqmi +uqmi +qmi-utils +modemmanager \
		+kmod-fs-vfat +kmod-fs-exfat +kmod-i2c-core +kmod-i2c-mt7628 \
		+kmod-nls-base +kmod-nls-cp437 +kmod-nls-iso8859-1 \
		+kmod-nls-iso8859-15 +kmod-nls-iso8859-2 +kmod-nls-utf8 \
		+kmod-sdhci-mt7620 +kmod-usb-storage +kmod-rtc-ds1307 \
		+tcpdump-mini 
	CATEGORY:=Base system
	DEFAULT:=y
endef

define Build/Prepare
	mkdir -p $(PKG_BUILD_DIR)
	mkdir -p $(TOPDIR)/files/etc/rc.button/
	if [ -f "./files/etc/rc.button/wps" ]; then \
		mv ./files/etc/rc.button/wps $(TOPDIR)/files/etc/rc.button/wps; \
	fi
	if [ -f "./files/etc/rc.local" ]; then \
		mv ./files/etc/rc.locl $(TOPDIR)/files/etc/rc.local; \
	fi
	$(call Build/Prepare/Default)
endef

define Build/Compile
	$(TARGET_CC) $(TARGET_CFLAGS) $(EXTRA_CFLAGS) -Wall -Werror -o $(PKG_BUILD_DIR)/pinmux src/pinmux.c ; \
	$(TARGET_CC) $(TARGET_CFLAGS) $(EXTRA_CFLAGS) -Wall -Werror -o $(PKG_BUILD_DIR)/refclk src/refclk.c
endef

define Package/mtk-linkit/install
	$(INSTALL_DIR) $(1)/sbin
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/pinmux $(1)/sbin/mt7688_pinmux
	$(INSTALL_BIN) $(PKG_BUILD_DIR)/refclk $(1)/sbin/mt7688_reclk
	$(CP) ./files/* $(1)/
endef

$(eval $(call BuildPackage,mtk-linkit))
