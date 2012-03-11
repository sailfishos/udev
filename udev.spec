#specfile originally created for Fedora, modified for Moblin Linux
%define udev_libdir /lib/udev
  
Summary:        A userspace implementation of devfs
Name:           udev
Version:        181
Release:        1
License:        GPLv2+
Group:          System/Base
Source0:        http://www.kernel.org/pub/linux/utils/kernel/hotplug/%{name}-%{version}.tar.xz

Source5:        udev.sysconfig
Source9:        80-clock.rules
Source12:       99-runtime-pm.rules
Source13:       oaktrail-ins

Patch0:         udev-177-tar-xz.patch

Patch101:       udev-116-nettype.patch
Patch102:       udev-118-sysconf.patch

Patch106:       udev-136-audio-video.patch
Patch109:       udev-input-needs-group.patch
Patch110:       udev-136-tty-group.patch
Patch112:       udev-pkgconfigdir.patch
Patch114:       udev-161-oaktrail-ins.patch

URL:            http://www.kernel.org/pub/linux/utils/kernel/hotplug/udev.html
Requires(pre):  fileutils
Requires:       mkdevnodes
Requires(post):   /bin/systemctl
Requires(preun):  /bin/systemctl
Requires(postun): /bin/systemctl
BuildRequires:  libtool
BuildRequires:  pkgconfig
BuildRequires:  gperf
BuildRequires:  pkgconfig(glib-2.0)
BuildRequires:  hwdata
BuildRequires:  pkgconfig(usbutils)
BuildRequires:  pkgconfig(blkid) >= 2.20
BuildRequires:  kmod-devel >= 5
Requires(pre):  fileutils
Requires(pre):  /usr/bin/getent /usr/sbin/groupadd
Requires:       hwdata
Requires:       util-linux >= 2.20

Obsoletes:      udev-extra
Requires:       systemd >= 38

%description
The udev package contains an implementation of devfs in 
userspace using sysfs and netlink.

%package rules-nondefault
Summary:        Udev rules not used in normal installs
Group:          System/base
Requires:       udev = %{version}-%{release}

%description rules-nondefault
This package contains a set of udev rules not used in normal installs

%package -n libudev
Summary:        Library for accessing udev functionality
Group:          Development/Libraries
Requires:       udev = %{version}-%{release}

%description -n libudev
This package contains a shared library for accesing libudev functionality.

%package -n libudev-devel
Summary:        Development files for libudev
Group:          Development/Libraries
Requires:       udev = %{version}-%{release}
Requires:       libudev = %{version}-%{release}

%description -n libudev-devel
This package contains libraries and include files, 
which needed to link against libudev.

%package -n libgudev1
Summary:        Libraries for adding libudev support to applications that use glib
Group:          Development/Libraries
Requires:       libudev = %{version}-%{release}
License:        LGPLv2+

%description -n libgudev1
This package contains the libraries that make it easier to use libudev
functionality from applications that use glib.

%package -n libgudev1-devel
Summary:        Header files for adding libudev support to applications that use glib
Group:          Development/Libraries
Requires:       libudev-devel = %{version}-%{release}
Requires:       libgudev1 = %{version}-%{release}
License:        LGPLv2+

%description -n libgudev1-devel
This package contains the header and pkg-config files for developing
glib-based applications using libudev functionality.

%prep
%setup -q

%patch0 -p1
%patch101 -p1 -b .nettyp
%patch102 -p1 -b .sysconf
%patch106 -p1 -b .video
%patch109 -p1 -b .groups
%patch110 -p1 -b .tty
%patch112 -p1 -b .datadir
%patch114 -p1 -b .okt


%build
autoreconf -v -f -i
%configure \
        --prefix=%{_prefix} \
        --with-rootprefix= \
        --sysconfdir=%{_sysconfdir} \
        --sbindir=/sbin \
        --libdir=%{_libdir} \
        --libexecdir=/lib \
        --with-rootlibdir=/%{_lib} \
        --disable-introspection \
        --with-systemdsystemunitdir=/%{_lib}/systemd/system

make %{?_smp_mflags}

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

mkdir -p $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig

rm -f $RPM_BUILD_ROOT/%{_libdir}/*.la
mkdir -p -m 0755 $RPM_BUILD_ROOT/lib/firmware
mkdir -p -m 0755 $RPM_BUILD_ROOT/lib/firmware/updates

# force relative symlinks
mkdir -p $RPM_BUILD_ROOT/sbin/
ln -sf /usr/bin/udevadm $RPM_BUILD_ROOT/sbin/udevadm

install -m 0644 %{SOURCE5} $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/udev
install -m 0644 %{SOURCE9} $RPM_BUILD_ROOT%{udev_libdir}/rules.d
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
systemctl reload-or-try-restart udev-settle.service
} || :
 
%preun
[ -x /bin/systemctl ] && {
systemctl stop udev.service
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

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(0644, root, root, 0755)
%doc COPYING README 
%attr(0755,root,root) /usr/bin/udevadm
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/udev/udev.conf
%attr(0755,root,root) /sbin/udevadm
%attr(0755,root,root) /lib/udev/udevd
%attr(0755,root,root) %dir %{udev_libdir}/rules.d/
%attr(0755,root,root) %dir %{_sysconfdir}/udev/
%attr(0755,root,root) %dir %{_sysconfdir}/udev/rules.d/
%attr(0755,root,root) %dir %{udev_libdir}/

%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/udev

%dir %attr(0755,root,root) /lib/firmware
%dir %attr(0755,root,root) /lib/firmware/updates
%attr(0644,root,root) /lib/systemd/system/*.service
%attr(0644,root,root) /lib/systemd/system/*.socket
/lib/systemd/system/basic.target.wants/*.service
/lib/systemd/system/sockets.target.wants/*.socket

%attr(0755,root,root) %{udev_libdir}/ata_id
%attr(0755,root,root) %{udev_libdir}/accelerometer
%attr(0755,root,root) %{udev_libdir}/cdrom_id
%attr(0755,root,root) %{udev_libdir}/collect
%attr(0755,root,root) %{udev_libdir}/findkeyboards
%attr(0755,root,root) %{udev_libdir}/keyboard-force-release.sh
%attr(0755,root,root) %{udev_libdir}/keymap
%attr(0755,root,root) %{udev_libdir}/keymaps/*
%attr(0755,root,root) %{udev_libdir}/scsi_id
%attr(0755,root,root) %{udev_libdir}/v4l_id
%attr(0755,root,root) %{udev_libdir}/mtd_probe
%doc /%{_datadir}/doc/udev/README.keymap.txt

%attr(0644,root,root) %{udev_libdir}/rules.d/*.rules
%attr(0644,root,root) %{_mandir}/man7/udev.7.gz
%attr(0644,root,root) %{_mandir}/man8/udevadm.8.gz
%attr(0644,root,root) %{_mandir}/man8/udevd.8.gz

%files rules-nondefault
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-storage-tape.rules
%attr(0755,root,root) %{udev_libdir}/rules.d/60-persistent-serial.rules

%files -n libudev
%defattr(0644, root, root, 0755)
%doc COPYING
%attr(0755,root,root) /%{_lib}/libudev.so.*

%files -n libudev-devel
%defattr(0644, root, root, 0755)
%attr(0644,root,root) %{_mandir}/man8/scsi_id*.8*
%{_includedir}/libudev.h
%{_libdir}/libudev.so
%{_libdir}/pkgconfig/libudev.pc
%{_libdir}/pkgconfig/udev.pc
%{_datadir}/gtk-doc/html/libudev/*

%files -n libgudev1
%defattr(0644, root, root, 0755)
%doc src/extras/gudev/COPYING
%attr(0755,root,root) /%{_lib}/libgudev-1.0.so.*

%files -n libgudev1-devel
%defattr(0644, root, root, 0755)
%attr(0755,root,root) %{_libdir}/libgudev-1.0.so
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0
%dir %attr(0755,root,root) %{_includedir}/gudev-1.0/gudev
%attr(0644,root,root) %{_includedir}/gudev-1.0/gudev/*.h
%dir %{_datadir}/gtk-doc/html/gudev
%attr(0644,root,root) %{_datadir}/gtk-doc/html/gudev/*
%attr(0644,root,root) %{_libdir}/pkgconfig/gudev-1.0*
