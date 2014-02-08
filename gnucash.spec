%define _disable_ld_no_undefined 1
%define major	0
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

%define doc_version 2.2.0
%define build_hbci 1

%if %{_use_internal_dependency_generator}
%define __noautoreq 'devel\\(libgncmod(.*)\\)|libgnc.*so$'
%endif

Summary:	Application to keep track of your finances
Name:		gnucash
Version:	2.4.12
Release:	4
License:	GPLv2+
Group:		Office
Url:		http://www.gnucash.org/
Source0:	http://downloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source2:	engine-common.i
Source4:	http://downloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.bz2
# (fc) 2.2.1-3mdv disable unneeded warning at startup (Fedora)
Patch0:		gnucash-quiet.patch
Patch1:		gnucash-2.4.11-link.patch
Patch2:		gnucash-docs-2.2.0-automake.patch

# build noise
Patch150:	gnucash-notsvn.patch
Patch151:	gnucash-2.4.12-swig_engine.patch

BuildRequires:	intltool
BuildRequires:	desktop-file-utils
BuildRequires:	rarian
BuildRequires:	slib
BuildRequires:	swig
BuildRequires:	xsltproc
BuildRequires:	dbi-devel
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(guile-1.8)
BuildRequires:	pkgconfig(ktoblzcheck)
BuildRequires:	pkgconfig(libglade-2.0)
BuildRequires:	pkgconfig(libgnomeui-2.0)
BuildRequires:	pkgconfig(libgoffice-0.8)
BuildRequires:	pkgconfig(libofx)
BuildRequires:	pkgconfig(webkit-1.0)
Requires:	guile1.8-runtime
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
cp %{SOURCE2} src/engine

export BUILDING_FROM_SVN=yes
autoreconf -fi

pushd gnucash-docs-%{doc_version}
autoreconf -fi
popd

%build
%configure2_5x \
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
%configure2_5x \
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
%doc %{_datadir}/%{name}/doc
%{_datadir}/%{name}/scm
%{_iconsdir}/hicolor/*/apps/gnucash*
%{_mandir}/*/*

%exclude %{_libdir}/gnucash/libgncmod-ofx*
%if %{build_hbci}
%exclude %{_libdir}/gnucash/libgncmod-aqbanking*
%exclude %{_datadir}/gnucash/glade/aqbanking*
%exclude %{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif
%exclude %{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%files ofx
%doc doc/README.OFX
%{_libdir}/gnucash/libgncmod-ofx*
%{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%if %{build_hbci}
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
%{_libdir}/lib*.so

%files -n %{devname}
%{_bindir}/gnucash-make-guids
%{_bindir}/gnucash-valgrind
%{_includedir}/gnucash

