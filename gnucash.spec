%define major 0
%define libname %mklibname %{name} %{major}
%define develname %mklibname -d %{name}

%define doc_version 2.2.0
%define build_hbci 1
Name: gnucash
Summary: Application to keep track of your finances
Version: 2.4.10
Release: 1
License: GPLv2+
Group: Office
URL: http://www.gnucash.org/
Source0: http://downloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source4: http://downloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.bz2
# (fc) 2.2.1-3mdv disable unneeded warning at startup (Fedora)
Patch0: gnucash-quiet.patch

BuildRequires: intltool
BuildRequires: desktop-file-utils
BuildRequires: libxslt-proc
BuildRequires: scrollkeeper
BuildRequires: slib
BuildRequires: guile-devel
BuildRequires: goffice-devel >= 0.7
BuildRequires: webkitgtk-devel
BuildRequires: dbi-devel
BuildRequires: libofx-devel >= 0.7.0
BuildRequires: libktoblzcheck-devel
BuildRequires: gettext-devel
BuildRequires: libgnomeui2-devel
BuildRequires: libglade2.0-devel

Requires: guile >= 1.6
Requires: slib
Requires: %{libname} >= %{version}-%{release}
Requires: yelp
Requires(post,postun): desktop-file-utils
Suggests: perl-Finance-Quote
%rename gnucash-sql

# MD this doesnt seem to be needed anymore
#disable requires in private shared libraries
#define _requires_exceptions devel.libgncmod-[^[:space:]].\\|libgnc-app

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

%if %build_hbci
%package hbci
Summary: Enables HBCI importing in GnuCash
Group: Office
Requires: gnucash = %{version}-%{release}
BuildRequires: libaqbanking-devel >= 3
# only require the wizard, it will pull aqhbci package too 
#gw it really required qt3-wizard which wasn't included in aqbanking for a while
Requires: aqhbci

%description hbci
This package adds HBCI file import support to the base
GnuCash package. Install this package if you want to
import HBCI files.
%endif

%package -n %{develname}
Group:	Development/C
Summary: Libraries needed to develop for gnucash
Requires: %{libname} = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}
Obsoletes: %{name}-devel %mklibname -d %{name} 0

%description -n %{develname}
Libraries needed to develop for gnucash.

%package -n %{libname}
Summary:        Libraries for gnucash
Group:          System/Libraries

%description -n %{libname}
This package provides libraries to use gnucash.

%prep
%setup -q -a 4
%apply_patches

%build
%define _disable_ld_no_undefined 1
%configure2_5x \
	--enable-gui \
	--enable-ofx \
	--disable-error-on-warning \
	--disable-schemas-install \
	--disable-static \
	--enable-locale-specific-tax \
	--enable-dbi \
	--with-html-engine=webkit \
%if %build_hbci
	--enable-aqbanking
%endif

cd gnucash-docs-%{doc_version}
%configure2_5x \
	--localstatedir=/var/lib
cd ..

make

cd gnucash-docs-%{doc_version}
%make
cd ..

%install
rm -rf %{buildroot} %{name}.lang
%makeinstall_std

cd gnucash-docs-%{doc_version}
%makeinstall_std
cd ..

rm -f %{buildroot}%{_infodir}/dir
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'

#don't ship this file
%{find_lang} %{name} --with-gnome --all-name
for omf in $(ls %{buildroot}%{_datadir}/omf/%{name}-docs/*.omf|fgrep -v -- -C.omf);do 
echo "%lang($(basename $omf|sed -e s/.*-// -e s/.omf//)) $(echo $omf|sed -e s!%{buildroot}!!)" >> %{name}.lang
done

# Menu entry 
desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --dir %{buildroot}%{_datadir}/applications %{buildroot}%{_datadir}/applications/*

# don't ship /usr/bin/gnc-test-env as it's only used for build and testing, this mitigates CVE-2010-3999
rm -f %{buildroot}%{_bindir}/gnc-test-env

%post
%define schemas apps_gnucash_dialog_business_common apps_gnucash_dialog_commodities apps_gnucash_dialog_common apps_gnucash_dialog_prices apps_gnucash_dialog_print_checks apps_gnucash_dialog_reconcile apps_gnucash_dialog_totd apps_gnucash_general apps_gnucash_history apps_gnucash_import_generic_matcher apps_gnucash_import_qif apps_gnucash_warnings apps_gnucash_window_pages_account_tree apps_gnucash_window_pages_register apps_gnucash_dialog_scheduled_transctions

%preun
%preun_uninstall_gconf_schemas %schemas

%if %build_hbci
%preun hbci
%preun_uninstall_gconf_schemas apps_gnucash_dialog_hbci
%endif

%files -f %{name}.lang
%doc AUTHORS COPYING HACKING NEWS README*
%doc doc/README.german doc/README.francais doc/guile-hackers.txt
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_business_common.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_commodities.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_common.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_prices.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_print_checks.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_reconcile.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_scheduled_transctions.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_totd.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_general.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_history.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_import_generic_matcher.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_import_qif.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_warnings.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_window_pages_account_tree.schemas
%{_sysconfdir}/gconf/schemas/apps_gnucash_window_pages_register.schemas
%config(noreplace) %{_sysconfdir}/%{name}		
%{_bindir}/gnucash
%{_bindir}/gnucash-env
%{_bindir}/gnc-fq-check
%{_bindir}/gnc-fq-dump
%{_bindir}/gnc-fq-helper
%{_bindir}/gnc-fq-update
%{_bindir}/update-gnucash-gconf
%{_datadir}/applications/%{name}.desktop
%dir %{_libdir}/gnucash
%{_libdir}/gnucash/*.so*
%{_libdir}/gnucash/overrides
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/accounts
%{_datadir}/%{name}/checks
%{_datadir}/%{name}/guile-modules
%{_datadir}/%{name}/glade
%{_datadir}/%{name}/pixmaps
%{_datadir}/%{name}/ui
%{_datadir}/%{name}/gnome
%{_datadir}/%{name}/tip_of_the_day.list
%{_datadir}/icons/hicolor/*/apps/gnucash*
%doc %{_datadir}/%{name}/doc
%{_datadir}/%{name}/scm
%{_mandir}/*/*
%dir %{_datadir}/omf/%{name}-docs/
%{_datadir}/omf/%{name}-docs/*.omf

%exclude %{_libdir}/gnucash/libgncmod-ofx*
%if %build_hbci
%exclude %{_libdir}/gnucash/libgncmod-aqbanking*
%exclude %{_datadir}/gnucash/glade/aqbanking*
%exclude %{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif
%exclude %{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%files ofx
%doc doc/README.OFX
%{_libdir}/gnucash/libgncmod-ofx*
%{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%if %build_hbci
%files hbci
%doc doc/README.HBCI
%{_sysconfdir}/gconf/schemas/apps_gnucash_dialog_hbci.schemas
%{_libdir}/gnucash/libgncmod-aqbanking*
%{_datadir}/gnucash/glade/aqbanking*
%{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif

%files -n %{libname}
%{_libdir}/libgnc-backend-sql.so.%{major}*
%{_libdir}/libgnc-backend-xml-utils.so.%{major}*
%{_libdir}/libgnc-business-ledger.so.%{major}*
%{_libdir}/libgnc-core-utils.so.%{major}*
%{_libdir}/libgnc-gnome.so.%{major}*
%{_libdir}/libgnc-module.so.%{major}*
%{_libdir}/libgnc-qof.so.1*

%files -n %{develname}
%{_bindir}/gnucash-make-guids
%{_bindir}/gnucash-valgrind
%{_libdir}/lib*.so
%{_includedir}/gnucash

