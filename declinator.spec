%global libmaj 1
%global desc_eng Automatised declension of names \
 \
Supported languages: \
 - Polish \
 - ... in spe: other slavic, lithuanian and hungarian
%global desc_pol Zautomatyzowana deklinacja nazwisk \
 \
Wspierane języki: \
 - polski \
 - ... wkrótce: inne słowiańskie, litewski i węgierski

Name:              declinator
Version:           %{libmaj}.0.1
Release:           1%{?dist}
Summary:           Automatized declension of names
Summary(pl.UTF-8): Zautomatyzowana deklinacja nazwisk
Group:             System/Internationalization
License:           AGPLv3+
URL:               https://github.com/Arusekk/declinator
Source0:           https://github.com/Arusekk/declinator/archive/v%{version}.tar.gz

BuildRequires:     pkgconfig(json-c) pkgconfig(libpcre)
Requires:          %{_lib}json2 libpcre

%description
%{desc_eng}

%description -l pl.UTF-8
%{desc_pol}


%package common
Summary:           Common files for declinator
Summary(pl.UTF-8): Wspólne pliki dla declinatora
BuildArch:         noarch

%description common
%{desc_eng}

This package contains common rules

%description -l pl.UTF-8 common
%{desc_pol}

Ten pakiet zawiera wspólne reguły

%files common
%license LICENSE.md
%doc README.md
%{_datadir}/declinator


%package -n %{_lib}declinator%{libmaj}
Summary:           Automatised declension of names
Summary(pl.UTF-8): Zautomatyzowana deklinacja nazwisk
Requires:          %{name}-common

%description -n %{_lib}declinator%{libmaj}
%{desc_eng}

This package contains the C library

%description -l pl.UTF-8 -n %{_lib}declinator%{libmaj}
%{desc_pol}

Ten pakiet zawiera bibliotekę C

%files -n %{_lib}declinator%{libmaj}
%{_libdir}/libdeclinator.so.%{libmaj}*
%{_bindir}/declinator


%package -n %{_lib}declinator-devel
Summary:           Development headers for declinator
Summary(pl.UTF-8): Nagłówki programistyczne dla declinatora
Requires:          pkgconfig(json-c) %{_lib}declinator%{libmaj}

%description -n %{_lib}declinator-devel
%{desc_eng}

This package contains development headers for the C library

%description -l pl.UTF-8 -n %{_lib}declinator-devel
%{desc_pol}

Ten pakiet zawiera nagłówki programistyczne dla biblioteki C

%files -n %{_lib}declinator-devel
%{_libdir}/libdeclinator.a
%{_libdir}/libdeclinator.la
%{_libdir}/libdeclinator.so
%{_includedir}/declinator.h


%package -n python3-%{name}
Summary:           Python interface for declinator
Summary(pl.UTF-8): Interfejs pythona dla declinatora
BuildArch:         noarch
BuildRequires:     pythonegg(3)(pip)
Requires:          pythonegg(3)(pip) %{name}-common

%description -n python3-%{name}
%{desc_eng}

This package contains python interface

%description -l pl.UTF-8 -n python3-%{name}
%{desc_pol}

Ten pakiet zawiera interfejs pythona

%files -n python3-%{name}
%{python3_sitelib}/declinator*


%prep
%setup

%build
cd c
mkdir -p .m4/m4
autoreconf -si
%GNUconfigure
%make_build
cd ../python
%py3_build
cd ..

%install
cd c
%make_install
cd ../python
%py3_install
cd ..


%changelog
* Tue May 15 2018 Arusekk <arek_koz@o2.pl>
- Initial RPM release
