%define lib_major 0
%define lib_name %mklibname %{name} %{lib_major}

%define gwrap_req_version 1.9.6-6mdv
%define doc_version 2.0.1

Name: gnucash
Summary: GnuCash is an application to keep track of your finances
Version: 2.0.5
Release: %mkrel 1
License: GPL
Group: Office
Source0: http://prdownloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source1: gnucash-48.png
Source2: gnucash-32.png
Source3: gnucash-16.png
Source4: http://prdownloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.bz2
BuildRoot: %{_tmppath}/%{name}-%{version}-buildroot
URL: http://www.gnucash.org

# g-wrap must be regenerated when guile is
Requires: guile >= 1.6
Requires: umb-scheme >= 3.2-17mdk
Requires: g-wrap >= %{gwrap_req_version}
#Requires: guile-lib
Requires: python >= 2.3
Requires: %{lib_name} >= %{version}-%{release}
Requires: yelp
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
#BuildRequires: guile-lib
BuildRequires: g-wrap-devel >= %{gwrap_req_version}
BuildRequires: goffice21-devel >= 0.0.4
BuildRequires: gtkhtml-3.8-compat-devel
BuildRequires: libgnomeprintui-devel
BuildRequires: readline-devel
BuildRequires: libtermcap-devel
BuildRequires: libxml-devel
BuildRequires: popt-devel
BuildRequires: python-devel >= 2.3
BuildRequires: scrollkeeper >= 0.3.4
BuildRequires: libxslt-proc
BuildRequires: libofx-devel >= 0.7.0
BuildRequires: libaqbanking-devel >= 1.0.0
BuildRequires: libktoblzcheck-devel
BuildRequires: postgresql-devel
BuildRequires: gettext-devel
BuildRequires: libffi-devel
BuildRequires: db1-devel
BuildRequires: intltool
BuildRequires: automake1.9
BuildRequires: desktop-file-utils
#disable requires in private shared libraries
%define _requires_exceptions devel.libgncmod-[^[:space:]].\\|libgnc-app\\|libgw-engine\\|libgw-kvp

%description
GnuCash is a personal finance manager. A check-book like
register GUI allows you to enter and track bank accounts,
stocks, income and even currency trades. The interface is
designed to be simple and easy to use, but is backed with
double-entry accounting principles to ensure balanced books.

%package ofx
Summary: Enables OFX importing in GnuCash
Group: Office
Requires: gnucash = %{version}-%{release}
 
%description ofx
This package adds OFX file import support to the base
GnuCash package. Install this package if you want to
import OFX files.

%package sql
Summary: PostgreSQL backend for GnuCash
Group: Office
Requires: gnucash = %{version}-%{release}
 
%description sql
This package adds PostgreSQL experimental backend for GnuCash.

%package hbci
Summary: Enables HBCI importing in GnuCash
Group: Office
Requires: gnucash = %{version}-%{release}
# only require the wizard, it will pull aqhbci package too 
Requires: aqhbci-qt-tools
 
%description hbci
This package adds HBCI file import support to the base
GnuCash package. Install this package if you want to
import HBCI files.


%package -n %{lib_name}-devel
Group:	Development/C
Summary: Libraries needed to develop for gnucash
Requires: %{lib_name} = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
Obsoletes: %{name}-devel


%description -n %{lib_name}-devel
Libraries needed to develop for gnucash.

%package -n %{lib_name}
Summary:        Libraries for gnucash
Group:          System/Libraries

%description -n %{lib_name}
This package provides libraries to use gnucash.


%prep
%setup -q -a 4
#libtoolize --force
#aclocal-1.9 -I macros
#automake-1.9
#autoconf

%build
#gw our libtool is older than the bundled one
%define __libtoolize true
%configure2_5x --enable-gui --enable-hbci --enable-ofx --disable-error-on-warning --enable-sql

cd gnucash-docs-%{doc_version}
%configure --localstatedir=/var/lib
cd ..

make

cd gnucash-docs-%{doc_version}
%make
cd ..

%install
rm -rf $RPM_BUILD_ROOT %name.lang

%makeinstall_std

cd gnucash-docs-%{doc_version}
%makeinstall_std
cd ..

# multiarch support
%multiarch_binaries $RPM_BUILD_ROOT%{_bindir}/gnucash-config

rm -f $RPM_BUILD_ROOT%{_infodir}/dir
find %buildroot -name \*.la|xargs chmod 644

#don't ship this file
%{find_lang} %{name} --with-gnome --all-name
for omf in $(ls %buildroot%_datadir/omf/%name-docs/*.omf|fgrep -v -- -C.omf);do 
echo "%lang($(basename $omf|sed -e s/.*-// -e s/.omf//)) $(echo $omf|sed -e s!%buildroot!!)" >> %name.lang
done


# Icons
mkdir -p $RPM_BUILD_ROOT/%{_iconsdir}
mkdir -p $RPM_BUILD_ROOT/%{_liconsdir}
mkdir -p $RPM_BUILD_ROOT/%{_miconsdir}
cp %{SOURCE1} $RPM_BUILD_ROOT/%{_liconsdir}/%{name}.png
cp %{SOURCE2} $RPM_BUILD_ROOT/%{_iconsdir}/%{name}.png
cp %{SOURCE3} $RPM_BUILD_ROOT/%{_miconsdir}/%{name}.png

# Menu entry 
mkdir -p $RPM_BUILD_ROOT/%{_menudir}
cat >$RPM_BUILD_ROOT/%{_menudir}/%{name} <<EOF
?package(%{name}): command="%{_bindir}/%{name}" icon="%{name}.png" needs="X11" \
section="More Applications/Finances" title="GnuCash" longtitle="GnuCash Personal finance manager" xdg="true"
EOF

desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --add-category="X-MandrivaLinux-MoreApplications-Finances" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*



%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post
%define schemas apps_gnucash_dialog_business_common apps_gnucash_dialog_commodities apps_gnucash_dialog_common apps_gnucash_dialog_hbci apps_gnucash_dialog_prices apps_gnucash_dialog_print_checks apps_gnucash_dialog_reconcile apps_gnucash_dialog_totd apps_gnucash_general apps_gnucash_history apps_gnucash_import_generic_matcher apps_gnucash_warnings apps_gnucash_window_pages_account_tree apps_gnucash_window_pages_register apps_gnucash_dialog_scheduled_transctions
%post_install_gconf_schemas %schemas
%{update_menus}
%update_desktop_database
%update_scrollkeeper

%preun
%preun_uninstall_gconf_schemas %schemas

%postun
%{clean_menus}
%clean_scrollkeeper
%clean_desktop_database

%post -n %{lib_name} -p /sbin/ldconfig
%postun -n %{lib_name} -p /sbin/ldconfig

%post -n %{lib_name}-devel
if [ "$1" = "1" ]; then 
  %{__install_info} %{_infodir}/%{name}-design.info.bz2 %{_infodir}/dir --section="Miscellaneous" --entry="* Gnucash: (gnucash-design).             Gnucash design."
fi

%postun -n %{lib_name}-devel
if [ "$1" = "0" ]; then
  %{__install_info} --delete %{_infodir}/%{name}-design.info.bz2 %{_infodir}/dir --section="Miscellaneous" --entry="* Gnucash: (gnucash-design).             Gnucash design."
fi

%files -n %{lib_name}-devel
%defattr(-,root,root)
%{_infodir}/*
%{_bindir}/gnucash-make-guids
%{_bindir}/gnucash-config
%multiarch %{multiarch_bindir}/gnucash-config
%{_libdir}/libcore-utils.so
%{_libdir}/libgnc-backend-file-utils.so
%{_libdir}/libgncgnome.so
%{_libdir}/libgncmodule.so
%{_libdir}/libgncqof.so
%{_libdir}/libgw-core-utils.so
%{_libdir}/libgw-gnc.so
%{_includedir}/gnucash
%{_datadir}/aclocal/*

%files -n %{lib_name}
%defattr(-, root, root)
%_libdir/libcore-utils.so.0*
%_libdir/libgnc-backend-file-utils.so.0*
%_libdir/libgncgnome.so.0*
%_libdir/libgncmodule.so.0*
%_libdir/libgncqof.so.1*
%_libdir/libgw-core-utils.so.0*
%_libdir/libgw-gnc.so.0*
# these are unversioned, bad gnucash developers
%{_libdir}/libgnc-backend-file.so
%{_libdir}/libgncqof-backend-qsf.so

%files -f %{name}.lang
%defattr(-,root,root)
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_business_common.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_commodities.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_common.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_hbci.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_prices.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_print_checks.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_reconcile.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_scheduled_transctions.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_totd.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_general.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_history.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_import_generic_matcher.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_warnings.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_window_pages_account_tree.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_window_pages_register.schemas
%config(noreplace) %{_sysconfdir}/%{name}		
%{_bindir}/gnucash
%{_bindir}/gnucash-bin
%{_bindir}/gnucash-valgrind
%{_bindir}/gnucash-env
%{_bindir}/gnc-test-env
%{_bindir}/gnc-fq-check
%{_bindir}/gnc-fq-dump
%{_bindir}/gnc-fq-helper
%{_bindir}/gnc-fq-update
%{_bindir}/update-gnucash-gconf
%_datadir/applications/%name.desktop
%_datadir/gnucash/
%dir %{_libdir}/gnucash
%{_libdir}/*.la
%{_libdir}/gnucash/*.la
%{_libdir}/gnucash/*.so*
%{_libdir}/gnucash/overrides
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/accounts
%{_datadir}/%{name}/guile-modules
%{_datadir}/%{name}/glade
%_datadir/pixmaps/gnucash-icon.png
%_datadir/xml/gnucash/
%doc %{_datadir}/%{name}/doc
%{_datadir}/%{name}/scm
%{_mandir}/*/*
%doc AUTHORS COPYING HACKING NEWS README*
%doc doc/README.german doc/README.francais doc/guile-hackers.txt
%{_iconsdir}/*.png
%{_miconsdir}/*.png
%{_liconsdir}/*.png
%{_menudir}/%{name}
%dir %{_datadir}/omf/%name-docs/
%{_datadir}/omf/%name-docs/gnucash-guide-C.omf
%{_datadir}/omf/%name-docs/gnucash-help-C.omf
%exclude %{_libdir}/gnucash/libgncmod-ofx*
%exclude %{_libdir}/gnucash/libgncmod-hbci*
%exclude %{_datadir}/gnucash/glade/hbci*

%files ofx
%defattr(-,root,root)
%doc doc/README.OFX
%{_libdir}/gnucash/libgncmod-ofx*

%files hbci
%defattr(-,root,root)
%doc doc/README.HBCI
%{_libdir}/gnucash/libgncmod-hbci*
%{_datadir}/gnucash/glade/hbci*

%files sql
%defattr(-,root,root)
%doc src/backend/postgres/README
%{_libdir}/libgnc-backend-postgres.so


