%global libmaj 1

Name:                 declinator
Version:              %{libmaj}.0.1
Release:              1%{?dist}
Summary:              Automatized declension of names
Summary(pl_PL.UTF-8): Zautomatyzowana deklinacja nazwisk
Group:                System/Internationalization
License:              AGPLv3+
URL:                  https://github.com/Arusekk/declinator
Source0:              https://github.com/Arusekk/declinator/archive/v%{version}.tar.gz

BuildRequires:        pkgconfig(json-c) pkgconfig(libpcre)
Requires:             %{_lib}json2 libpcre

%description
Automatised declension of names

Supported languages:
 - Polish
 - ... in spe: other slavic, lithuanian and hungarian

%description -l pl_PL.UTF-8
Zautomatyzowana deklinacja nazwisk

Wspierane języki:
 - polski
 - ... wkrótce: inne słowiańskie, litewski i węgierski

%package common
Summary:              Common files for declinator
Summary(pl_PL.UTF=8): Wspólne pliki dla declinatora

%description common
This package contains common files

%files common
%license LICENSE.md
%doc README.md
%{_datadir}/declinator

%package -n %{_lib}declinator%{libmaj}
Summary:              Automatised declension of names
Summary(pl_PL.UTF-8): Zautomatyzowana deklinacja nazwisk
Requires:             %{name}-common

%files -n %{_lib}declinator%{libmaj}
%{_libdir}/libdeclinator.so.%{libmaj}*
%{_bindir}/declinator

%description -n %{_lib}declinator%{libmaj}
This package contains the C library

%package -n %{_lib}declinator-devel
Summary:              Development headers for declinator
Summary(pl_PL.UTF-8): Nagłówki programistyczne dla declinatora
Requires:             pkgconfig(json-c) %{_lib}declinator%{libmaj}

%description -n %{_lib}declinator-devel
This package contains development headers

%files -n %{_lib}declinator-devel
%{_libdir}/libdeclinator.a
%{_libdir}/libdeclinator.la
%{_libdir}/libdeclinator.so
%{_includedir}/declinator.h

%package -n python3-%{name}
Summary:              Python interface for declinator
Summary(pl_PL.UTF-8): Interfejs pythona dla declinatora
BuildArch:            noarch
BuildRequires:        pythonegg(3)(pip)
Requires:             pythonegg(3)(pip) %{name}-common

%description -n python3-%{name}
This package contains python interface

%files -n python3-%{name}
%{python3_sitelib}/declinator*


%prep
%autosetup

%build
pushd c
mkdir -p .m4/m4
autoreconf -si
%GNUconfigure
%make_build
popd
pushd python
%py3_build
popd

%install
pushd c
%make_install
popd
pushd python
%py3_install
popd


%changelog
* Tue May 15 2018 Arek <rpm@glus>
- Initial RPM release
