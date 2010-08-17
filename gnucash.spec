%define lib_major 0
%define libname %mklibname %{name} %{lib_major}
%define libnamedev %mklibname -d %{name}

%define doc_version 2.2.0
%define build_hbci 0
Name: gnucash
Summary: Application to keep track of your finances
Version: 2.2.9
Release: %mkrel 7
License: GPLv2+
Group: Office
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-buildroot
Source0: http://prdownloads.sourceforge.net/gnucash/%{name}-%{version}.tar.lzma
Source4: http://prdownloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.bz2
# (fc) 2.2.1-3mdv disable unneeded warning at startup (Fedora)
Patch0: gnucash-quiet.patch
#gw rediffed from svn
Patch1: gnucash-2.2.9-fix-build-with-new-goffice.patch
URL: http://www.gnucash.org/

Requires: guile >= 1.6
Requires: slib
Requires: python >= 2.3
Requires: %{libname} >= %{version}-%{release}
Requires: yelp
Requires(post): desktop-file-utils
Requires(postun): desktop-file-utils
Suggests: perl-Finance-Quote
BuildRequires: guile-devel
BuildRequires: goffice-devel >= 0.7
BuildRequires: gtkhtml-3.14-devel
BuildRequires: readline-devel
BuildRequires: libtermcap-devel
BuildRequires: popt-devel
BuildRequires: python-devel >= 2.3
BuildRequires: scrollkeeper >= 0.3.4
BuildRequires: libxslt-proc
BuildRequires: libofx-devel >= 0.7.0
BuildRequires: libktoblzcheck-devel
BuildRequires: postgresql-devel
BuildRequires: gettext-devel
BuildRequires: libffi-devel
BuildRequires: libgnomeui2-devel
BuildRequires: libglade2.0-devel
BuildRequires: intltool
BuildRequires: automake
BuildRequires: desktop-file-utils
BuildRequires: slib
#disable requires in private shared libraries
%define _requires_exceptions devel.libgncmod-[^[:space:]].\\|libgnc-app

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

%if %build_hbci
%package hbci
Summary: Enables HBCI importing in GnuCash
Group: Office
Requires: gnucash = %{version}-%{release}
BuildRequires: libaqbanking-devel >= 3
# only require the wizard, it will pull aqhbci package too 
#gw it really required qt3-wizard which wasn't included in aqbanking for a while
Requires: aqbanking-qt4

 
%description hbci
This package adds HBCI file import support to the base
GnuCash package. Install this package if you want to
import HBCI files.
%endif

%package -n %{libnamedev}
Group:	Development/C
Summary: Libraries needed to develop for gnucash
Requires: %{libname} = %{version}-%{release}
Provides: %{name}-devel = %{version}-%{release}
Provides: lib%{name}-devel = %{version}-%{release}
Obsoletes: %{name}-devel %mklibname -d %name 0


%description -n %{libnamedev}
Libraries needed to develop for gnucash.

%package -n %{libname}
Summary:        Libraries for gnucash
Group:          System/Libraries

%description -n %{libname}
This package provides libraries to use gnucash.


%prep
%setup -q -a 4
%patch0 -p1 -b .quiet
%patch1 -p1 -b .goffice

aclocal -I macros
libtoolize --copy --force
autoconf
automake

%build
%configure2_5x --enable-gui  --enable-ofx --disable-error-on-warning --enable-sql --disable-schemas-install \
%if %build_hbci
--enable-hbci
%endif


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


rm -f $RPM_BUILD_ROOT%{_infodir}/dir
find %buildroot -name \*.la|xargs chmod 644

#don't ship this file
%{find_lang} %{name} --with-gnome --all-name
for omf in $(ls %buildroot%_datadir/omf/%name-docs/*.omf|fgrep -v -- -C.omf);do 
echo "%lang($(basename $omf|sed -e s/.*-// -e s/.omf//)) $(echo $omf|sed -e s!%buildroot!!)" >> %name.lang
done



# Menu entry 
desktop-file-install --vendor="" \
  --remove-category="Application" \
  --add-category="GTK" \
  --dir $RPM_BUILD_ROOT%{_datadir}/applications $RPM_BUILD_ROOT%{_datadir}/applications/*


%clean
[ -n "$RPM_BUILD_ROOT" -a "$RPM_BUILD_ROOT" != "/" ] && rm -rf $RPM_BUILD_ROOT

%post
%define schemas apps_gnucash_dialog_business_common apps_gnucash_dialog_commodities apps_gnucash_dialog_common apps_gnucash_dialog_prices apps_gnucash_dialog_print_checks apps_gnucash_dialog_reconcile apps_gnucash_dialog_totd apps_gnucash_general apps_gnucash_history apps_gnucash_import_generic_matcher apps_gnucash_import_qif apps_gnucash_warnings apps_gnucash_window_pages_account_tree apps_gnucash_window_pages_register apps_gnucash_dialog_scheduled_transctions

%preun
%preun_uninstall_gconf_schemas %schemas

%if %build_hbci
%preun hbci
%preun_uninstall_gconf_schemas apps_gnucash_dialog_hbci
%endif


%post -n %{libnamedev}
if [ "$1" = "1" ]; then 
  %{__install_info} %{_infodir}/%{name}-design.info.bz2 %{_infodir}/dir --section="Miscellaneous" --entry="* Gnucash: (gnucash-design).             Gnucash design."
fi

%postun -n %{libnamedev}
if [ "$1" = "0" ]; then
  %{__install_info} --delete %{_infodir}/%{name}-design.info.bz2 %{_infodir}/dir --section="Miscellaneous" --entry="* Gnucash: (gnucash-design).             Gnucash design."
fi

%files -n %{libnamedev}
%defattr(-,root,root)
%{_infodir}/*
%{_bindir}/gnucash-make-guids
%{_libdir}/libgnc-backend-file-utils.so
%_libdir/libgnc-business-ledger.so
%_libdir/libgnc-core-utils.so
%_libdir/libgnc-gnome.so
%_libdir/libgnc-module.so
%_libdir/libgnc-qof.so
%{_includedir}/gnucash

%files -n %{libname}
%defattr(-, root, root)
%_libdir/libgnc-backend-file-utils.so.0*
%_libdir/libgnc-business-ledger.so.0*
%_libdir/libgnc-core-utils.so.0*
%_libdir/libgnc-gnome.so.0*
%_libdir/libgnc-module.so.0*
%_libdir/libgnc-qof.so.1*


%files -f %{name}.lang
%defattr(-,root,root)
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_business_common.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_commodities.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_common.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_prices.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_print_checks.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_reconcile.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_scheduled_transctions.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_totd.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_general.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_history.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_import_generic_matcher.schemas
%_sysconfdir/gconf/schemas/apps_gnucash_import_qif.schemas
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
%_datadir/icons/hicolor/*/apps/gnucash*
%_datadir/xml/gnucash/
%doc %{_datadir}/%{name}/doc
%{_datadir}/%{name}/scm
%{_mandir}/*/*
%doc AUTHORS COPYING HACKING NEWS README*
%doc doc/README.german doc/README.francais doc/guile-hackers.txt
%dir %{_datadir}/omf/%name-docs/
%{_datadir}/omf/%name-docs/gnucash-guide-C.omf
%{_datadir}/omf/%name-docs/gnucash-help-C.omf
%exclude %{_libdir}/gnucash/libgncmod-ofx*
%if %build_hbci
%exclude %{_libdir}/gnucash/libgncmod-aqbanking*
%exclude %{_datadir}/gnucash/glade/aqbanking*
%exclude %{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif
%exclude %{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%files ofx
%defattr(-,root,root)
%doc doc/README.OFX
%{_libdir}/gnucash/libgncmod-ofx*
%{_datadir}/gnucash/ui/gnc-plugin-ofx-ui.xml

%if %build_hbci
%files hbci
%defattr(-,root,root)
%doc doc/README.HBCI
%_sysconfdir/gconf/schemas/apps_gnucash_dialog_hbci.schemas
%{_libdir}/gnucash/libgncmod-aqbanking*
%{_datadir}/gnucash/glade/aqbanking*
%{_datadir}/gnucash/ui/gnc-plugin-aqbanking-ui.xml
%endif

%files sql
%defattr(-,root,root)
%doc src/backend/postgres/README
%{_libdir}/libgnc-backend-postgres.so


