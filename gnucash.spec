%define _disable_ld_no_undefined 1
%define major 0
%define libname %mklibname %{name} %{major}
%define develname %mklibname -d %{name}

%define doc_version 2.2.0
%define build_hbci 1

%if %{_use_internal_dependency_generator}
%define __noautoreq 'devel\\(libgncmod(.*)\\)'
%endif

Name:		gnucash
Summary:	Application to keep track of your finances
Version:	2.4.12
Release:	1
License:	GPLv2+
Group:		Office
URL:		http://www.gnucash.org/
Source0:	http://downloads.sourceforge.net/gnucash/%{name}-%{version}.tar.bz2
Source2:	engine-common.i
Source4:	http://downloads.sourceforge.net/gnucash/%{name}-docs-%{doc_version}.tar.bz2
# (fc) 2.2.1-3mdv disable unneeded warning at startup (Fedora)
Patch0:		gnucash-quiet.patch
Patch1:		gnucash-2.4.11-link.patch

# Guile 2.0 support (from Fedora)
Patch101:	gnucash-guile-1.patch
Patch102:	gnucash-guile-2.patch
Patch103:	gnucash-guile-3.patch
Patch104:	gnucash-guile-4.patch
Patch105:	gnucash-guile-5.patch
Patch106:	gnucash-guile-6.patch
Patch107:	gnucash-guile-7.patch
Patch108:	gnucash-guile-8.patch
Patch109:	gnucash-guile-9.patch

# build noise
Patch150:	gnucash-notsvn.patch

BuildRequires:	intltool
BuildRequires:	desktop-file-utils
BuildRequires:	libxslt-proc
BuildRequires:	scrollkeeper
BuildRequires:	slib
BuildRequires:	swig
BuildRequires:	pkgconfig(guile-2.0)
BuildRequires:	pkgconfig(libgoffice-0.8)
BuildRequires:	pkgconfig(webkit-1.0)
BuildRequires:	dbi-devel
BuildRequires:	pkgconfig(libofx)
BuildRequires:	pkgconfig(ktoblzcheck)
BuildRequires:	gettext-devel
BuildRequires:	pkgconfig(libgnomeui-2.0)
BuildRequires:	pkgconfig(libglade-2.0)

Requires:	guile >= 1.6
Requires:	slib
Requires:	%{libname} >= %{version}-%{release}
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

%package -n %{develname}
Group:		Development/C
Summary:	Libraries needed to develop for gnucash
Requires:	%{libname} = %{version}-%{release}
Provides:	%{name}-devel = %{version}-%{release}

%description -n %{develname}
Libraries needed to develop for gnucash.

%package -n %{libname}
Summary:	Libraries for gnucash
Group:		System/Libraries

%description -n %{libname}
This package provides libraries to use gnucash.

%prep
%setup -q -a 4
%patch0 -p1
%patch1 -p0
%patch101 -p1
%patch102 -p1
%patch103 -p1
%patch104 -p1
%patch105 -p1
%patch106 -p1
%patch107 -p1
%patch108 -p1
%patch109 -p1
%patch150 -p1
cp %{SOURCE2} src/engine

%build
export BUILDING_FROM_SVN=yes
autoreconf -fi
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
%if %{build_hbci}
	--enable-aqbanking
%endif

pushd gnucash-docs-%{doc_version}
%configure2_5x \
	--localstatedir=/var/lib
popd

make

pushd gnucash-docs-%{doc_version}
%make
popd

%install
%makeinstall_std

pushd gnucash-docs-%{doc_version}
%makeinstall_std
popd

rm -f %{buildroot}%{_infodir}/dir
find %{buildroot} -type f -name "*.la" -exec rm -f {} ';'

%{find_lang} %{name} --with-gnome --all-name

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

%files -n %{develname}
%{_bindir}/gnucash-make-guids
%{_bindir}/gnucash-valgrind
%{_libdir}/lib*.so
%{_includedir}/gnucash



%changelog
* Mon Mar 26 2012 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.10-1
+ Revision: 786956
- update omf file list
- fix goffice build deps
- new version
- drop patch 1

* Mon Jan 16 2012 Matthew Dawkins <mattydaw@mandriva.org> 2.4.9-1
+ Revision: 761822
- readd scrollkeeper for docs
- added new source 2.4.9
- new version 2.4.9
- cleaned up spec
- removed .la files from main pkg
- cleaned up BRs

* Mon Nov 28 2011 Matthew Dawkins <mattydaw@mandriva.org> 2.4.8-1
+ Revision: 735074
- added p1 for glib.h build error

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - new version

* Mon Jul 11 2011 GÃ¶tz Waschk <waschk@mandriva.org> 2.4.7-1
+ Revision: 689506
- update to new version 2.4.7

* Mon Jun 20 2011 Funda Wang <fwang@mandriva.org> 2.4.6-2
+ Revision: 686113
- rebuild for new webkit

* Sat May 28 2011 Funda Wang <fwang@mandriva.org> 2.4.6-1
+ Revision: 680397
- update to new version 2.4.6

* Mon May 23 2011 Funda Wang <fwang@mandriva.org> 2.4.5-2
+ Revision: 677721
- rebuild to add gconftool as req

* Mon Apr 11 2011 Funda Wang <fwang@mandriva.org> 2.4.5-1
+ Revision: 652567
- update to new version 2.4.5

* Fri Mar 18 2011 Jani VÃ¤limaa <wally@mandriva.org> 2.4.4-1
+ Revision: 646396
- new version 2.4.4

* Mon Feb 28 2011 Funda Wang <fwang@mandriva.org> 2.4.3-1
+ Revision: 640716
- new version 2.4.3

* Wed Feb 09 2011 Funda Wang <fwang@mandriva.org> 2.4.2-1
+ Revision: 636961
- enable aqbanking
- new version 2.4.2

* Thu Dec 23 2010 Funda Wang <fwang@mandriva.org> 2.4.0-1mdv2011.0
+ Revision: 624086
- new version 2.4.0

* Sun Dec 05 2010 Oden Eriksson <oeriksson@mandriva.com> 2.3.17-2mdv2011.0
+ Revision: 609659
- rebuilt against new libdbi

* Thu Nov 25 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.3.17-1mdv2011.0
+ Revision: 601002
- update to new version 2.3.17

* Wed Nov 24 2010 Oden Eriksson <oeriksson@mandriva.com> 2.3.15-2mdv2011.0
+ Revision: 600715
- fix CVE-2010-3999

* Thu Sep 02 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.3.15-1mdv2011.0
+ Revision: 575225
- new version
- update file list

* Tue Aug 31 2010 Funda Wang <fwang@mandriva.org> 2.3.14-2mdv2011.0
+ Revision: 574595
- rebuild for new gwenhywfar

* Tue Aug 17 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.3.14-1mdv2011.0
+ Revision: 570961
- new development version
- rediff patch
- drop patch 1
- reenable hbci plugin
- obsolete sql backend
- depend on webkit and on libdbi
- update file list
- disable hbci support, our aqbanking is too new

  + Funda Wang <fwang@mandriva.org>
    - rebuild for new popt

* Sun Feb 14 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-6mdv2010.1
+ Revision: 505820
- rebuild for new goffice

* Fri Feb 12 2010 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-5mdv2010.1
+ Revision: 504706
- depend on qt4 aqbanking

* Thu Sep 24 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-4mdv2010.0
+ Revision: 448346
- update build deps
- update patch 1 for new goffice

* Wed Jun 03 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-3mdv2010.0
+ Revision: 382354
- rebuild for new aqbanking

* Wed May 20 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-2mdv2010.0
+ Revision: 377967
- fix build with new goffice
- disable schemas installation

  + Frederik Himpe <fhimpe@mandriva.org>
    - Add Suggests: perl-Finance-Quote for online retrieval of quotes

* Tue Feb 24 2009 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.9-1mdv2009.1
+ Revision: 344483
- update to new version 2.2.9

* Tue Dec 16 2008 Funda Wang <fwang@mandriva.org> 2.2.8-1mdv2009.1
+ Revision: 314725
- New version 2.2.8
- underlinking problem fixed by upstream

* Sun Nov 09 2008 Oden Eriksson <oeriksson@mandriva.com> 2.2.7-2mdv2009.1
+ Revision: 301591
- rebuilt against new libxcb

* Sat Oct 11 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.7-1mdv2009.1
+ Revision: 292466
- new version
- call libtoolize

* Thu Jul 31 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.6-1mdv2009.0
+ Revision: 257782
- new version
- drop patch 1
- update build deps
- fix buildrequires for goffice 0.6

  + Pixel <pixel@mandriva.com>
    - rpm filetriggers deprecates update_menus/update_scrollkeeper/update_mime_database/update_icon_cache/update_desktop_database/post_install_gconf_schemas
    - do not call ldconfig in %%post/%%postun, it is now handled by filetriggers

* Mon Jun 02 2008 Frederik Himpe <fhimpe@mandriva.org> 2.2.5-2mdv2009.0
+ Revision: 214364
- Add patch to fix underlinking in gnome-utils subdir by linking with libX11
- Add patch to fix underlinking in file backend
- Fix license
- Remove libxml-devel: this is the old libxml1 library, which is not used by gnucash. libxml2-devel is already implicitely required by gtkhtml-devel

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - new version
    - update schemas list

* Wed Apr 23 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.4-2mdv2009.0
+ Revision: 196752
- patch for aqbanking 3.x

* Wed Mar 05 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.4-1mdv2008.1
+ Revision: 180054
- new version

  + Thierry Vignaud <tv@mandriva.org>
    - fix gtkhtml-3.14-devel BuildRequires
    - rebuild
    - fix "foobar is blabla" summary (=> "blabla") so that it looks nice in rpmdrake
    - fix no-buildroot-tag

* Thu Jan 10 2008 Frederic Crozat <fcrozat@mandriva.com> 2.2.3-2mdv2008.1
+ Revision: 147649
- Force rebuild with latest GConf

* Thu Jan 10 2008 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.3-1mdv2008.1
+ Revision: 147516
- new version
- drop patch
- update file list
- update icon theme in postinstall

* Sat Dec 22 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.2-3mdv2008.1
+ Revision: 136851
- patch to build with goffice 0.6

  + Olivier Blin <blino@mandriva.org>
    - restore BuildRoot

* Tue Dec 18 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.2-2mdv2008.1
+ Revision: 132333
- rebuild for new goffice

* Tue Dec 18 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.2-1mdv2008.1
+ Revision: 132108
- new version
- build with goffice 0.5

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request

* Wed Nov 28 2007 Frederic Crozat <fcrozat@mandriva.com> 2.2.1-3mdv2008.1
+ Revision: 113756
- Patch0 (Fedora): disable unneeded warning at startup
- Remove old menu file
- Replace dependency on umb-scheme with slib dependency (Fedora)

* Mon Sep 24 2007 Frederic Crozat <fcrozat@mandriva.com> 2.2.1-2mdv2008.0
+ Revision: 92510
- Fix build

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - fix buildrequires

* Mon Aug 20 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.1-1mdv2008.0
+ Revision: 67902
- new version

* Fri Aug 10 2007 Frederic Crozat <fcrozat@mandriva.com> 2.2.0-2mdv2008.0
+ Revision: 61594
- Remove dependency on g-wrap
- Fix icon name

  + GÃ¶tz Waschk <waschk@mandriva.org>
    - drop external icons

* Mon Jul 16 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.2.0-1mdv2008.0
+ Revision: 52486
- new version
- update buildrequires
- fix file list
- new devel package name
- drop buildrequires on libunicode, it is dead


* Tue Mar 06 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.0.5-1mdv2007.0
+ Revision: 133834
- new version
- fix buildrequires
- *** empty log message ***
- depend on yelp (bug #28547)

  + Thierry Vignaud <tvignaud@mandriva.com>
    - no need to package big ChangeLog when NEWS is already there

* Sun Jan 07 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.0.4-2mdv2007.1
+ Revision: 105229
- rebuild

* Wed Jan 03 2007 GÃ¶tz Waschk <waschk@mandriva.org> 2.0.4-1mdv2007.1
+ Revision: 103507
- new version

* Mon Dec 18 2006 GÃ¶tz Waschk <waschk@mandriva.org> 2.0.3-1mdv2007.1
+ Revision: 98663
- disable libtoolize

  + Frederic Crozat <fcrozat@mandriva.com>
    - Release 2.0.3

* Tue Oct 17 2006 GÃ¶tz Waschk <waschk@mandriva.org> 2.0.2-2mdv2007.1
+ Revision: 65561
- rebuild
- Import gnucash

* Sat Oct 14 2006 Götz Waschk <waschk@mandriva.org> 2.0.2-1mdv2007.1
- update source URL
- new version

* Thu Aug 03 2006 Götz Waschk <waschk@mandriva.org> 2.0.1-1mdv2007.0
- update file list
- New release 2.0.1

* Wed Jul 19 2006 Götz Waschk <waschk@mandriva.org> 2.0.0-2mdv2007.0
- use shared goffice again
- drop valgrind conflict
- rebuild with new gail

* Tue Jul 11 2006 Götz Waschk <waschk@mandriva.org> 2.0.0-1mdv2007.0
- fix source URLs
- New release 2.0.0

* Fri Jun 23 2006 Götz Waschk <waschk@mandriva.org> 1.9.8-2mdv2007.0
- split out postgres backend
- move .la files to main package
- move all libraries to the lib package
- fix deps

* Wed Jun 21 2006 Götz Waschk <waschk@mandriva.org> 1.9.8-1mdv2007.0
- use new macros
- fix menu
- New release 1.9.8

* Fri Jun 16 2006 Götz Waschk <waschk@mandriva.org> 1.9.7-1mdv2007.0
- xdg menu
- update file list
- disable valgrind
- don't depend on guile-lib
- new version

* Wed May 17 2006 Götz Waschk <waschk@mandriva.org> 1.9.6-1mdk
- update file list
- New release 1.9.6

* Thu Apr 20 2006 GÃ¶tz Waschk <waschk@mandriva.org> 1.9.5-1mdk
- New release 1.9.5

* Sat Apr 08 2006 GÃ¶tz Waschk <waschk@mandriva.org> 1.9.4-1mdk
- New release 1.9.4

* Thu Apr 06 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.9.3-3mdk
- rebuild with rpm-mandriva-setup 1.18 to fix requires

* Sat Apr 01 2006 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.9.3-2mdk
- add BuildRequires: libffi-devel db1-devel

* Tue Mar 21 2006 GÃ¶tz Waschk <waschk@mandriva.org> 1.9.3-1mdk
- update file list
- New release 1.9.3

* Tue Mar 07 2006 Götz Waschk <waschk@mandriva.org> 1.9.2-2mdk
- use the right configure macro
- rebuild for new aqbanking

* Tue Mar 07 2006 Götz Waschk <waschk@mandriva.org> 1.9.2-1mdk
- schemas are no configuration files
- New release 1.9.2

* Sun Feb 26 2006 Götz Waschk <waschk@mandriva.org> 1.9.1-2mdk
- depend on guile-lib

* Mon Feb 20 2006 Götz Waschk <waschk@mandriva.org> 1.9.1-1mdk
- drop patches
- New release 1.9.1
- use mkrel

* Mon Jan 16 2006 Frederic Crozat <fcrozat@mandriva.com> 1.8.12-1mdk
- Release 1.8.12
- Regenerate patch0, remove old libtool m4 macros

* Mon Dec 05 2005 GÃ¶tz Waschk <waschk@mandriva.org> 1.8.11-4mdk
- rebuild for new aqbanking

* Thu Jun 16 2005 Frederic Lepied <flepied@mandriva.com> 1.8.11-3mdk
- rebuild for libpq

* Thu Apr 07 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 1.8.11-2mdk 
- Rebuild with new aqhbci (Mdk bug #13985)

* Thu Feb 24 2005 Frederic Crozat <fcrozat@mandrakesoft.com> 1.8.11-1mdk 
- Release 1.8.11

* Sun Feb 20 2005 Christiaan Welvaart <cjw@daneel.dyndns.org> 1.8.10-3mdk
- multiarch

* Wed Dec 29 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.8.10-2mdk 
- hbci subpackage now requires aqhbci-wizard-kde (only config wizard available
  now). Fix Mdk bug #12782
- Move info files to devel package (they are devel doc), Mdk bug #12106.
- Enable experimental postgresql support (Mdk bug #12499)

* Mon Dec 13 2004 Götz Waschk <waschk@linux-mandrake.com> 1.8.10-1mdk
- fix omf file listing
- update the docs
- depend on aqbanking instead of openhbci
- bump ofx dep
- New release 1.8.10

* Sat Aug 14 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.8.9-2mdk
- Rebuild for new gcc

* Fri May 14 2004 Frederic Crozat <fcrozat@mandrakesoft.com> 1.8.9-1mdk
- New release 1.8.9
- Update docs to 1.8.4

