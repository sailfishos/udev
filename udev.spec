#specfile originally created for Fedora, modified for Moblin Linux
%define udev_libdir /lib/udev
%define firmwaredir /lib/firmware
  
Summary: A userspace implementation of devfs
Name: udev
Version: 172
Release: 1
License: GPLv2
Group: System/Base
Source0: http://www.us.kernel.org/pub/linux/utils/kernel/hotplug/%{name}-%{version}.tar.bz2

Source1: start_udev
Source2: udev.nodes
Source4: fw_unit_symlinks.sh
Source5: udev.sysconfig
Source9: 80-clock.rules
Source11: 60-filesystem-info.rules
Source12: 99-runtime-pm.rules
Source13: oaktrail-ins

Patch101: udev-116-nettype.patch
Patch102: udev-118-sysconf.patch

Patch106: udev-136-audio-video.patch
Patch109: udev-input-needs-group.patch
Patch110: udev-136-tty-group.patch
Patch111: udev-145-reconf.patch
Patch112: udev-pkgconfigdir.patch
Patch114: udev-161-oaktrail-ins.patch

ExclusiveOS: Linux
URL: http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html
Requires(pre): /bin/sh fileutils
Requires(pre): /usr/bin/stat 
Requires(pre): MAKEDEV >= 0:3.11
Requires: hwdata
Requires: MAKEDEV 
Requires: sed 
Requires: pam 
Requires: mkdevnodes

Requires(post):   /bin/systemctl
Requires(preun):  /bin/systemctl
Requires(postun): /bin/systemctl
BuildRequires: sed flex 
BuildRequires: hwdata 
BuildRequires: pam-devel
BuildRequires: libacl-devel libusb-devel
BuildRequires: bison findutils
BuildRequires: gperf libtool
BuildRequires: pkgconfig(glib-2.0)
BuildRequires: pkgconfig(usbutils)

Obsoletes: udev-extra

%description
The udev package contains an implementation of devfs in 
userspace using sysfs and netlink.

%package rules-nondefault
Summary: Udev rules not used in normal installs
Group: System/base
Requires: udev = %{version}-%{release}

%description rules-nondefault
This package contains a set of udev rules not used in normal installs

%package -n libudev
Summary: Library for accessing udev functionality
Group: Development/Libraries
Requires: udev = %{version}-%{release}

%description -n libudev
This package contains a shared library for accesing libudev functionality.

%package -n libudev-devel
Summary: Headers for libudev
Group: Development/Libraries
Requires: udev = %{version}-%{release}
Requires: libudev = %{version}-%{release}

%description -n libudev-devel
This package contains libraries and include files, 
which needed to link against libudev.

%package -n libgudev1
Summary: Libraries for adding libudev support to applications that use glib
Group: Development/Libraries
Requires: libudev >= 142
# remove the following lines for libgudev so major 1
Provides: libgudev = 20090517
Obsoletes: libgudev <= 20090516
 
%description -n libgudev1
This package contains the libraries that make it easier to use libudev
functionality from applications that use glib.
 
%package -n libgudev1-devel
Summary: Header files for adding libudev support to applications that use glib
Group: Development/Libraries
Requires: libudev-devel >= 142
Provides: libgudev-devel = 20090517
Obsoletes: libgudev-devel <= 20090516
 
Requires: libgudev1 = %{version}-%{release}
 
%description -n libgudev1-devel
This package contains the header and pkg-config files for developing
glib-based applications using libudev functionality.
 
%prep
%setup -q

%patch101 -p1 -b .nettyp
%patch102 -p1 -b .sysconf
%patch106 -p1 -b .video
%patch109 -p1 -b .groups
%patch110 -p1 -b .tty
%patch111 -p1 -b .ref
%patch112 -p1 -b .datadir
%patch114 -p1 -b .okt


%build
libtoolize -f -c
%configure --prefix=%{_prefix} --exec-prefix="" \
           --sysconfdir=%{_sysconfdir} --with-libdir-name=%{_lib} \
           --sbindir="/sbin" --libexecdir=%{udev_libdir} \
           --with-rootlibdir=/%{_lib} --disable-introspection \
           --with-systemdsystemunitdir="/%{_lib}/systemd/system"

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT

make DESTDIR=$RPM_BUILD_ROOT install
mkdir -p \
    $RPM_BUILD_ROOT%{_sysconfdir}/udev/{makedev.d,scripts,devices} \
    $RPM_BUILD_ROOT%{_sysconfdir}/dev.d \
    $RPM_BUILD_ROOT%{firmwaredir} \
    $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig \
    $RPM_BUILD_ROOT/var/lib/udev/makedev.d \
    $RPM_BUILD_ROOT%{_bindir} \
    $RPM_BUILD_ROOT%{_sbindir} \
    $RPM_BUILD_ROOT/usr/lib/pkgconfig \
    $RPM_BUILD_ROOT/%{_libdir}/ConsoleKit/run-session.d \
    $RPM_BUILD_ROOT%{udev_libdir}/{,devices}

rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la

# force relative symlinks
ln -sf ..%{udev_libdir}/scsi_id $RPM_BUILD_ROOT/sbin/scsi_id

ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT%{_bindir}/udevinfo
ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT%{_bindir}/udevtest
ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT%{_sbindir}/udevmonitor

ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT/sbin/udevtrigger
ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT/sbin/udevsettle
ln -sf ../../sbin/udevadm $RPM_BUILD_ROOT/sbin/udevcontrol


install -m 0644 %{SOURCE2} $RPM_BUILD_ROOT%{_sysconfdir}/udev/makedev.d/50-udev.nodes
install -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/udev
install -m 0755 %{SOURCE1} $RPM_BUILD_ROOT/sbin/start_udev
install -m 0755 %{SOURCE4} $RPM_BUILD_ROOT%{udev_libdir}/fw_unit_symlinks.sh
install -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{udev_libdir}/rules.d
install -m 0644 %{SOURCE11} $RPM_BUILD_ROOT%{udev_libdir}/rules.d
install -m 0644 %{SOURCE12} $RPM_BUILD_ROOT%{udev_libdir}/rules.d
install -m 0644 %{SOURCE13} $RPM_BUILD_ROOT%{udev_libdir}/keymaps

%pre
getent group video >/dev/null || /usr/sbin/groupadd -g 39 video || :
getent group audio >/dev/null || /usr/sbin/groupadd -g 63 audio || :
# to be kept
getent group cdrom >/dev/null || /usr/sbin/groupadd -g 11 cdrom || :
getent group tape >/dev/null || /usr/sbin/groupadd -g 33 tape || :
getent group dialout >/dev/null || /usr/sbin/groupadd -g 18 dialout || :

%post
[ -x /bin/systemctl ] && {
systemctl daemon-reload
systemctl reload-or-try-restart udev.service
systemctl reload-or-try-restart udev-retry.service
systemctl reload-or-try-restart udev-settle.service
} || :
 
%preun
[ -x /bin/systemctl ] && {
systemctl stop udev.service
systemctl stop udev-retry.service
systemctl stop udev-settle.service
} || :
 
%postun
[ -x /bin/systemctl ] && {
systemctl stop udev.service
systemctl daemon-reload
} || :

%post -n libudev -p /sbin/ldconfig
%postun -n libudev -p /sbin/ldconfig

%post -n libgudev1 -p /sbin/ldconfig
%postun -n libgudev1 -p /sbin/ldconfig


%triggerpostun -- dev <= 0:3.12-1
if [ $2 = 0 ]; then
        if [ -x /sbin/MAKEDEV ]; then 
                /sbin/MAKEDEV null
        else
                /bin/mknod /dev/null c 1 3
        fi
        /sbin/start_udev >/dev/null 2>&1
        if [ -e /dev/mapper/control -a -x /sbin/lvm ]; then
                /sbin/lvm vgmknodes >/dev/null 2>&1
        fi
fi
exit 0


%triggerin -- MAKEDEV
rm -f /var/lib/udev/makenode.d/*  >/dev/null 2>&1 || :

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root, 0755)
%doc COPYING README 
%attr(0755,root,root) /sbin/udevadm
%attr(0755,root,root) /sbin/udevsettle
%attr(0755,root,root) /sbin/udevtrigger
%attr(0755,root,root) /sbin/udevcontrol
%attr(0755,root,root) /sbin/udevd
%attr(0755,root,root) /sbin/start_udev
%attr(0755,root,root) /sbin/scsi_id
%attr(0755,root,root) %{_bindir}/udevtest
%attr(0755,root,root) %{_bindir}/udevinfo
%attr(0755,root,root) %{_sbindir}/udevmonitor
%attr(0755,root,root) %dir %{udev_libdir}/rules.d/
%attr(0755,root,root) %dir %{_sysconfdir}/udev/
%attr(0755,root,root) %dir %{_sysconfdir}/udev/rules.d/
%attr(0755,root,root) %dir %{udev_libdir}/
%attr(0755,root,root) %dir %{udev_libdir}/devices/
%attr(0755,root,root) %dir %{_sysconfdir}/udev/makedev.d/

%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/udev

%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/udev/udev.conf

%dir %attr(0755,root,root) %{firmwaredir}

%dir %attr(0755,root,root) /var/lib/udev
%dir %attr(0755,root,root) /var/lib/udev/makedev.d

# Deprecated, but keep the ownership
%ghost %dir %{_sysconfdir}/udev/scripts/
%ghost %dir %{_sysconfdir}/udev/devices/
%ghost %dir %{_sysconfdir}/dev.d/

%attr(0644,root,root) %{_prefix}/lib/ConsoleKit/run-seat.d/udev-acl.ck


/etc/udev/makedev.d/50-udev.nodes
%attr(0755,root,root) %{udev_libdir}/ata_id
%attr(0755,root,root) %{udev_libdir}/accelerometer
%attr(0755,root,root) %{udev_libdir}/input_id
%attr(0755,root,root) %{udev_libdir}/cdrom_id
%attr(0755,root,root) %{udev_libdir}/collect
%attr(0755,root,root) %{udev_libdir}/findkeyboards
%attr(0755,root,root) %{udev_libdir}/keyboard-force-release.sh
%attr(0755,root,root) %{udev_libdir}/firmware
%attr(0755,root,root) %{udev_libdir}/fw_unit_symlinks.sh
%attr(0755,root,root) %{udev_libdir}/keymap
%attr(0755,root,root) %{udev_libdir}/keymaps/*
%attr(0755,root,root) %{udev_libdir}/path_id
%attr(0755,root,root) %{udev_libdir}/pci-db
%attr(0644,root,root) %{udev_libdir}/rule_generator.functions
%attr(0755,root,root) %{udev_libdir}/scsi_id
%attr(0755,root,root) %{udev_libdir}/udev-acl
%attr(0755,root,root) %{udev_libdir}/usb-db
%attr(0755,root,root) %{udev_libdir}/usb_id
%attr(0755,root,root) %{udev_libdir}/v4l_id
%attr(0755,root,root) %{udev_libdir}/write_cd_rules
%attr(0755,root,root) %{udev_libdir}/write_net_rules
%attr(0755,root,root) %{udev_libdir}/mtd_probe
%doc /%{_datadir}/doc/udev/README.keymap.txt
#%doc /%{_datadir}/doc/udev/writing_udev_rules/index.html

%attr(0755,root,root) %{udev_libdir}/rules.d/42-qemu-usb.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/50-firmware.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/50-udev-default.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-cdrom_id.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-alsa.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-v4l.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-input.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-storage.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-filesystem-info.rules
#%attr(0755,root,root) %{udev_libdir}/rules.d/61-option-modem-modeswitch.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/61-accelerometer.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/70-acl.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/75-cd-aliases-generator.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/75-net-description.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/75-tty-description.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/75-probe_mtd.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/78-sound-card.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/80-clock.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/80-drivers.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/95-keyboard-force-release.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/95-keymap.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/95-udev-late.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/99-runtime-pm.rules

/%{_lib}/systemd/system/basic.target.wants/udev.service
/%{_lib}/systemd/system/udev.service
/%{_lib}/systemd/system/basic.target.wants/udev-trigger.service
/%{_lib}/systemd/system/sockets.target.wants/udev-control.socket
/%{_lib}/systemd/system/sockets.target.wants/udev-kernel.socket
/%{_lib}/systemd/system/udev-control.socket
/%{_lib}/systemd/system/udev-kernel.socket
/%{_lib}/systemd/system/udev-settle.service
/%{_lib}/systemd/system/udev-trigger.service


%files rules-nondefault
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-storage-tape.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/75-persistent-net-generator.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-serial.rules

%files -n libudev
%defattr(0644, root, root, 0755)
%doc libudev/COPYING
%attr(0755,root,root) /%{_lib}/libudev.so.*

%files -n libudev-devel
%defattr(0644, root, root, 0755)
%doc libudev/COPYING
%doc TODO ChangeLog extras/keymap/README.keymap.txt
%attr(0644,root,root) %{_mandir}/man8/udev*.8*
%attr(0644,root,root) %{_mandir}/man7/udev*.7*
%attr(0644,root,root) %{_mandir}/man8/scsi_id*.8*
%{_includedir}/libudev.h
%{_libdir}/libudev.so
%{_libdir}/pkgconfig/libudev.pc
%{_libdir}/pkgconfig/udev.pc
%{_datadir}/gtk-doc/html/libudev/*


%files -n libgudev1
%defattr(0644, root, root, 0755)
%doc extras/gudev/COPYING
%attr(0755,root,root) /%{_lib}/libgudev-1.0.so.*

%files -n libgudev1-devel
%defattr(0644, root, root, 0755)
%doc extras/gudev/COPYING
%attr(0755,root,root) %{_libdir}/libgudev-1.0.so
%attr(0644,root,root) %{_includedir}/gudev-1.0/gudev/*.h
%dir %{_datadir}/gtk-doc/html/gudev
%attr(0644,root,root) %{_datadir}/gtk-doc/html/gudev/*
%attr(0644,root,root) %{_libdir}/pkgconfig/gudev-1.0*
 
