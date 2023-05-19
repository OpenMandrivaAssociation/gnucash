%define _disable_ld_no_undefined 1
%define major	0
%define libname %mklibname %{name} %{major}
%define devname %mklibname -d %{name}

%define doc_version 5.1
%define build_hbci 1
%global guileapi 3.0

%define _cmake_skip_rpath %nil

%define __noautoreq 'devel\\(libgncmod(.*)\\)|libgnc.*so$|devel\\(lib(gnc|cairo|gdk|glib|gmodule|gobject|gtk|guile|m|pango|xml2|z)(.*)\\)'
%define __noautoprov 'devel\\(libgnc(.*)\\)'

Summary:	Application to keep track of your finances
Name:		gnucash
Version:	5.1
Release:	1
License:	GPLv2+
Group:		Office
Url:		http://www.gnucash.org/
Source0:	http://downloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source4:	http://downloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.gz
Source100:	gnucash.rpmlintrc
BuildRequires:	cmake ninja
BuildRequires:	desktop-file-utils
BuildRequires:	rarian
BuildRequires:	slib
BuildRequires:	swig
BuildRequires:	xsltproc
BuildRequires:	dbi-devel
BuildRequires:	libdbi-drivers-dbd-sqlite3
BuildRequires:  libdbi-drivers-dbd-mysql
BuildRequires:  libdbi-drivers-dbd-pgsql
BuildRequires:	gettext-devel
BuildRequires:	guile guile-runtime
BuildRequires:	pkgconfig(atomic_ops)
BuildRequires:  pkgconfig(dbi) >= 0.9.0
BuildRequires:	pkgconfig(ktoblzcheck)
BuildRequires:	pkgconfig(libofx)
BuildRequires:	pkgconfig(webkit2gtk-4.1)
BuildRequires:	pkgconfig(gtk+-3.0)
BuildRequires:	pkgconfig(libxslt)
BuildRequires:	pkgconfig(libxml-2.0)
BuildRequires:  pkgconfig(guile-%{guileapi})
BuildRequires:	pkgconfig(libsecret-1)
BuildRequires:  gtest-devel
BuildRequires:  gtest-source
BuildRequires:	boost-devel
BuildRequires:	gmp-devel
BuildRequires:	strace
# guile sucks
BuildRequires:	locales-extra-charsets
Requires:	libdbi-drivers-dbd-sqlite3
Requires:	guile-runtime
Requires:	locales-extra-charsets
Requires:	slib
Requires:	yelp
Requires:	%{libname} = %{version}-%{release}
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
%autopatch -p1

sed -e 's|-Werror||g' -i CMakeLists.txt

%build
# Let's try to see what's wrong with guile detection
# if and only if running inside abf...
strace -f guile --version
echo -n "Guile prefix is: "
guile -c "(display (assoc-ref %%guile-build-info 'prefix))"

# set HAVE_GWEN_GTK3 as it tries to build its own otherwise
# but we have necessary patches in gwenhywfar
%cmake -DHAVE_GWEN_GTK3=1 -DCOMPILE_GSCHEMAS=OFF -DGNC_DBD_DIR=%{_libdir}/dbd -G Ninja || :
if ! [ -e build.ninja ]; then
	cat CMakeFiles/CMakeError.log
	cat CMakeFiles/CMakeOutput.log
	exit 1
fi

%ninja_build

cd ..

pushd gnucash-docs-%{doc_version}
%cmake
%make_build
popd

%install
%ninja_install -C build

pushd gnucash-docs-%{doc_version}
%make_install -C build
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

rm -f %{buildroot}%{_datadir}/glib-2.0/schemas/gschemas.compiled

%preun
%preun_uninstall_gconf_schemas %schemas

%if %build_hbci
%preun hbci
%preun_uninstall_gconf_schemas apps_gnucash_dialog_hbci
%endif

%files -f %{name}.lang
%doc %{_datadir}/doc/gnucash/*
%doc %{_datadir}/gnucash-docs/		
%{_datadir}/glib-2.0/schemas/org.gnucash.GnuCash.*
%config(noreplace) %{_sysconfdir}/%{name}
%{_bindir}/gnucash
%{_bindir}/gnucash-cli
%{_bindir}/gnc-fq-update
%{_bindir}/finance-quote-wrapper	
%{_datadir}/applications/%{name}.desktop
%{_datadir}/guile/site/%{guileapi}/%{name}
%dir %{_libdir}/gnucash
%{_libdir}/gnucash/*.so*
%{_libdir}/guile/%{guileapi}/site-ccache/gnucash/
%dir %{_datadir}/%{name}
%{_datadir}/%{name}/accounts
%{_datadir}/%{name}/chartjs
%{_datadir}/%{name}/checks
%{_datadir}/%{name}/gtkbuilder
%{_datadir}/%{name}/icons
%{_datadir}/%{name}/pixmaps
%{_datadir}/gnucash/ui/
%{_datadir}/%{name}/tip_of_the_day.list
%{_datadir}/metainfo/gnucash.appdata.xml
%{_datadir}/gnucash/pref_transformations.xml
%{_iconsdir}/hicolor/*/apps/gnucash*
%{_mandir}/*/*

#exclude %{_libdir}/gnucash/libgncmod-ofx*
#if %{build_hbci}
#exclude %{_libdir}/gnucash/libgncmod-aqbanking*
#exclude %{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
#endif
#exclude %{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%files ofx
#{_libdir}/gnucash/libgncmod-ofx*
#{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%if %{build_hbci}
%files hbci
#{_libdir}/gnucash/libgncmod-aqbanking*
#{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif

%files -n %{libname}
%{_libdir}/lib*.so

%files -n %{devname}
%{_bindir}/gnucash-valgrind
%{_includedir}/gnucash

