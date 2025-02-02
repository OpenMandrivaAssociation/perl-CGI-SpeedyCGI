%define upstream_name	 CGI-SpeedyCGI
%define upstream_version 2.22

%define Werror_cflags %{nil}

#Module-Specific definitions
%define apache_version 2.2.9
%define mod_name mod_speedycgi
%define mod_conf B49_%{mod_name}.conf
%define mod_so %{mod_name}.so

Name:		perl-%{upstream_name}
Version:	%perl_convert_version %{upstream_version}
Release:	6

Summary:	Speed up perl scripts by running them persistently
License:	GPLv3+
Group:		Development/Perl
Url:		https://search.cpan.org/dist/%{upstream_name}
Source0:	http://www.cpan.org/modules/by-authors/id/H/HO/HORROCKS/%{upstream_name}-%{upstream_version}.tar.gz
Source1:	%{mod_conf}
Patch0:		perl-CGI-SpeedyCGI-2.22-documentation.patch
Patch1:		perl-CGI-SpeedyCGI-2.22-empty_param.patch
Patch2:		perl-CGI-SpeedyCGI-2.22-strerror.patch
Patch3:		perl-CGI-SpeedyCGI-2.22-brigade_foreach.patch
Patch4:		perl-CGI-SpeedyCGI-2.22-exit_messages.patch
Patch5:		perl-CGI-SpeedyCGI-2.22-perl_510.patch
Patch6:		perl-CGI-SpeedyCGI-2.22-force-apache2.patch

BuildRequires:	perl-devel
BuildRequires:	perl(ExtUtils::MakeMaker)
BuildRequires:	perl(ExtUtils::Embed)
BuildRequires:	apache-devel >= %{apache_version}

%description
SpeedyCGI is a way to run perl scripts persistently, which can make them run
much more quickly. A script can be made to to run persistently by changing the
interpreter line at the top of the script from:
    #!/usr/bin/perl
to
    #!/usr/bin/speedy
After the script is initially run, instead of exiting, the perl interpreter is
kept running. During subsequent runs, this interpreter is used to handle new
executions instead of starting a new perl interpreter each time. A very fast
frontend program, written in C, is executed for each request. This fast
frontend then contacts the persistent Perl process, which is usually already
running, to do the work and return the results.

%package -n	apache-%{mod_name}
Summary:	SpeedyCGI module for the Apache HTTP Server
Group:		System/Servers
Requires(pre): rpm-helper
Requires(postun): rpm-helper
Requires(pre):  apache-conf >= %{apache_version}
Requires(pre):  apache >= %{apache_version}
Requires:	apache-conf >= %{apache_version}
Requires:	apache >= %{apache_version}
Requires:	%{name} = %{version}-%{release}

%description -n	apache-%{mod_name}
The SpeedyCGI module for the Apache HTTP Server. It can be used to run perl
scripts for web application persistently to make them more quickly.

%prep
%setup -q -n %{upstream_name}-%{upstream_version}
%patch0 -p1 -b .documentation
%patch1 -p1 -b .empty_param
%patch2 -p1 -b .strerror
%patch3 -p1 -b .brigade_foreach
%patch4 -p1 -b .exit_messages
%patch5 -p1 -b .perl_510
%patch6 -p1 -b .apache2

cp %{SOURCE1} %{mod_conf}

%build
%serverbuild

sed -i 's@apxs -@%{_bindir}/apxs -@g' Makefile.PL src/SpeedyMake.pl \
  mod_speedycgi/t/ModTest.pm mod_speedycgi/t/mod_perl.t
sed -i 's@APXS=apxs@APXS=%{_bindir}/apxs@g' mod_speedycgi/Makefile.tmpl

echo yes | perl Makefile.PL INSTALLDIRS=vendor
make OPTIMIZE="$CFLAGS" LDFLAGS="%{ldflags}"

#check
##- this test does not work with 5.8.7.
#rm speedy/t/be_memleak.t
#make test

%install
make pure_install PERL_INSTALL_ROOT=%{buildroot}

install -d %{buildroot}%{_libdir}/apache-extramodules
install -d %{buildroot}%{_sysconfdir}/httpd/modules.d

install -m0755 mod_speedycgi2/.libs/*.so %{buildroot}%{_libdir}/apache-extramodules/
install -m0644 %{mod_conf} %{buildroot}%{_sysconfdir}/httpd/modules.d/%{mod_conf}

%post -n apache-%{mod_name}
if [ -f %{_var}/lock/subsys/httpd ]; then
    %{_initrddir}/httpd restart 1>&2;
fi

%postun -n apache-%{mod_name}
if [ "$1" = "0" ]; then
    if [ -f %{_var}/lock/subsys/httpd ]; then
        %{_initrddir}/httpd restart 1>&2
    fi
fi

%files
%doc Changes README docs contrib util
%{perl_vendorlib}/CGI/*
%{_bindir}/speedy*

%files -n apache-%{mod_name}
%attr(0644,root,root) %config(noreplace) %{_sysconfdir}/httpd/modules.d/%{mod_conf}
%attr(0755,root,root) %{_libdir}/apache-extramodules/%{mod_so}


%changelog
* Sat May 28 2011 Funda Wang <fwang@mandriva.org> 2.220.0-3mdv2011.0
+ Revision: 680699
- mass rebuild

* Sun Oct 24 2010 Oden Eriksson <oeriksson@mandriva.com> 2.220.0-2mdv2011.0
+ Revision: 588140
- rebuild

* Sat Aug 01 2009 Jérôme Quelin <jquelin@mandriva.org> 2.220.0-1mdv2011.0
+ Revision: 406870
- rebuild using %%perl_convert_version

* Wed Jan 07 2009 Oden Eriksson <oeriksson@mandriva.com> 2.22-8mdv2009.1
+ Revision: 326701
- rebuild

* Sat Oct 11 2008 Guillaume Rousse <guillomovitch@mandriva.org> 2.22-7mdv2009.1
+ Revision: 292555
- force apache2 mod building
- fix buildrequires
- rebuild for linking

  + Oden Eriksson <oeriksson@mandriva.com>
    - sync slightly with fedora

  + Thierry Vignaud <tv@mandriva.org>
    - rebuild

* Fri Dec 21 2007 Olivier Blin <oblin@mandriva.com> 2.22-3mdv2008.1
+ Revision: 136678
- restore BuildRoot

  + Thierry Vignaud <tv@mandriva.org>
    - kill re-definition of %%buildroot on Pixel's request


* Thu Mar 08 2007 Thierry Vignaud <tvignaud@mandriva.com> 2.22-3mdv2007.1
+ Revision: 138542
- rebuild on dbarth request

  + Guillaume Rousse <guillomovitch@mandriva.org>
    - Import perl-CGI-SpeedyCGI

* Tue Jun 27 2006 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 2.22-2mdv2007.0
- Rebuild for new perl

* Fri Jul 01 2005 Rafael Garcia-Suarez <rgarciasuarez@mandriva.com> 2.22-1mdk
- Initial Mandriva release

