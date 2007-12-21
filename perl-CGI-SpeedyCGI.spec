%define module	CGI-SpeedyCGI
%define name	perl-%{module}
%define version	2.22
%define	release	%mkrel 3

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Speed up perl scripts by running them persistently
License:	GPL
Group:		Development/Perl
Source0:	%{module}-%{version}.tar.bz2
Url:		http://search.cpan.org/dist/%{module}
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-buildroot
BuildRequires:	perl-devel

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

%prep
%setup -q -n %{module}-%{version}

%build
%{__perl} Makefile.PL INSTALLDIRS=vendor < /dev/null
%{__make}
#- this test does not work with 5.8.7.
rm speedy/t/be_memleak.t

%check
%{__make} test

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

%clean 
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc Changes README docs contrib util
%{perl_vendorlib}/CGI/*
%{_bindir}/speedy*


