%define _disable_ld_no_undefined 1
%define major	0
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

%define doc_version 2.6.13
%define build_hbci 1

%define __noautoreq 'devel\\(libgncmod(.*)\\)|libgnc.*so$|devel\\(lib(gnc|cairo|gdk|glib|gmodule|gobject|gtk|guile|m|pango|xml2|z)(.*)\\)'
%define __noautoprov 'devel\\(libgnc(.*)\\)'

Summary:	Application to keep track of your finances
Name:		gnucash
Version:	2.6.13
Release:	1
License:	GPLv2+
Group:		Office
Url:		http://www.gnucash.org/
Source0:	http://downloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source4:	http://downloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.gz
Source100:	gnucash.rpmlintrc

BuildRequires:	intltool
BuildRequires:	desktop-file-utils
BuildRequires:	rarian
BuildRequires:	slib
BuildRequires:	swig
BuildRequires:	xsltproc
BuildRequires:	dbi-devel
BuildRequires:	libdbi-drivers-dbd-sqlite3
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(guile-2.0)
BuildRequires:	pkgconfig(ktoblzcheck)
BuildRequires:	pkgconfig(libglade-2.0)
BuildRequires:	pkgconfig(libgoffice-0.8)
BuildRequires:	pkgconfig(libofx)
BuildRequires:	pkgconfig(webkit-1.0)
BuildRequires:	pkgconfig(libgnomecanvas-2.0)
Requires:	libdbi-drivers-dbd-sqlite3
Requires:	guile-runtime
Requires:	slib
Requires:	yelp
Suggests:	perl-Finance-Quote
%rename gnucash-sql

%description
GnuCash is a personal finance manager. A check-book like
register GUI allows you to enter and track bank accounts,
stocks, income and even currency trades. The interface is
designed to be simple and easy to use, but is backed with
double-entry accounting principles to ensure balanced books.

%package ofx
Summary:	Enables OFX importing in GnuCash
Group:		Office
Requires:	%{name} = %{version}-%{release}

%description ofx
This package adds OFX file import support to the base
GnuCash package. Install this package if you want to
import OFX files.

%if %{build_hbci}
%package hbci
Summary:	Enables HBCI importing in GnuCash
Group:		Office
Requires:	%{name} = %{version}-%{release}
BuildRequires:	pkgconfig(aqbanking)
# only require the wizard, it will pull aqhbci package too 
#gw it really required qt3-wizard which wasn't included in aqbanking for a while
Requires:	aqhbci

%description hbci
This package adds HBCI file import support to the base
GnuCash package. Install this package if you want to
import HBCI files.
%endif

%package -n %{devname}
Group:		Development/C
Summary:	Libraries needed to develop for gnucash
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{devname}
Libraries needed to develop for gnucash.

%package -n %{libname}
Summary:	Libraries for gnucash
Group:		System/Libraries

%description -n %{libname}
This package provides libraries to use gnucash.

%prep
%setup -q -a 4
%apply_patches

%build
%configure \
	--enable-gui \
	--enable-ofx \
	--disable-error-on-warning \
	--disable-schemas-install \
	--disable-static \
	--enable-locale-specific-tax \
	--enable-dbi \
	--with-html-engine=webkit \
%if %{build_hbci}
	--enable-aqbanking
%endif

pushd gnucash-docs-%{doc_version}
%configure \
	--localstatedir=/var/lib
popd

make

pushd gnucash-docs-%{doc_version}
make
popd

%install
%makeinstall_std

pushd gnucash-docs-%{doc_version}
%makeinstall_std
popd

rm -f %{buildroot}%{_infodir}/dir

%{find_lang} %{name} --with-gnome --all-name
rm -fr %{buildroot}%{_libexecdir}/gnucash/src/libqof/qof/test

# Menu entry
desktop-file-install --vendor="" \
	--remove-category="Application" \
	--add-category="GTK" \
	--dir %{buildroot}%{_datadir}/applications \
	%{buildroot}%{_datadir}/applications/*

# don't ship /usr/bin/gnc-test-env as it's only used for build and testing, this mitigates CVE-2010-3999
rm -f %{buildroot}%{_bindir}/gnc-test-env

#%post
#%define schemas apps_gnucash_dialog_business_common apps_gnucash_dialog_commodities apps_gnucash_dialog_common apps_gnucash_dialog_prices apps_gnucash_dialog_print_checks apps_gnucash_dialog_reconcile apps_gnucash_dialog_totd apps_gnucash_general apps_gnucash_history apps_gnucash_import_generic_matcher apps_gnucash_import_qif apps_gnucash_warnings apps_gnucash_window_pages_account_tree apps_gnucash_window_pages_register apps_gnucash_dialog_scheduled_transctions

%preun
%preun_uninstall_gconf_schemas %schemas

%if %build_hbci
%preun hbci
%preun_uninstall_gconf_schemas apps_gnucash_dialog_hbci
%endif

%files -f %{name}.lang
%doc AUTHORS COPYING HACKING NEWS README*
%doc doc/README.german doc/README.francais doc/guile-hackers.txt
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.business.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.checkprinting.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.commodities.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.export.csv.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.import.csv.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.import.generic.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.import.qif.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.reconcile.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.sxs.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.totd.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.history.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.warnings.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.window.pages.account.tree.gschema.xml
%{_datadir}/glib-2.0/schemas/org.gnucash.window.pages.gschema.xml
%config(noreplace) %{_sysconfdir}/%{name}
%{_bindir}/gnucash
%{_bindir}/gnucash-env
%{_bindir}/gnc-fq-check
%{_bindir}/gnc-fq-dump
%{_bindir}/gnc-fq-helper
%{_bindir}/gnc-fq-update
%{_datadir}/applications/%{name}.desktop
%{_libexecdir}/%{name}/overrides/*
%dir %{_libdir}/gnucash
%{_libdir}/gnucash/*.so*
%{_libdir}/%{name}/scm
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/accounts
%{_datadir}/%{name}/checks
%{_datadir}/%{name}/gtkbuilder
%{_datadir}/%{name}/jqplot
%{_datadir}/%{name}/pixmaps
%{_datadir}/%{name}/ui
%{_datadir}/%{name}/gnome
%{_datadir}/%{name}/tip_of_the_day.list
%{_datadir}/%{name}/make-prefs-migration-script.xsl
%{_datadir}/%{name}/migratable-prefs.xml
%{_datadir}/%{name}/scm
%{_datadir}/appdata/gnucash.appdata.xml
%{_iconsdir}/hicolor/*/apps/gnucash*
%{_mandir}/*/*

%exclude %{_libdir}/gnucash/libgncmod-ofx*
%if %{build_hbci}
%exclude %{_libdir}/gnucash/libgncmod-aqbanking*
%exclude %{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif
%exclude %{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%files ofx
%doc doc/README.OFX
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.import.ofx.gschema.xml
%{_libdir}/gnucash/libgncmod-ofx*
%{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%if %{build_hbci}
%files hbci
%doc doc/README.HBCI
%{_datadir}/glib-2.0/schemas/org.gnucash.dialogs.import.hbci.gschema.xml
%{_libdir}/gnucash/libgncmod-aqbanking*
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
%{_libdir}/lib*.so

%files -n %{devname}
%{_bindir}/gnucash-make-guids
%{_bindir}/gnucash-valgrind
%{_includedir}/gnucash

