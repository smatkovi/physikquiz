Name: harbour-physikquiz
Version: 0.1.0
Release: 1
Summary: Physik-Quiz im Stil von Quizduell
License: Proprietary (private use)
URL: https://github.com/smatkovi/harbour-physikquiz
Source0: %{name}-%{version}.tar.gz

Requires:       sailfishsilica-qt5
Requires:       qt5-qtimageformats-plugin-webp
BuildRequires:  pkgconfig(sailfishapp)
BuildRequires:  pkgconfig(Qt5Core)
BuildRequires:  pkgconfig(Qt5DBus)
BuildRequires:  pkgconfig(Qt5Network)
BuildRequires:  pkgconfig(Qt5Qml)
BuildRequires:  pkgconfig(Qt5Quick)
BuildRequires:  cmake

%description
PhysikQuiz is a physics quiz in the style of Quizduell with questions from
Austrian school books. Play against the computer or against friends in the
same Wi-Fi network; choose one school level or all of them.

%prep
%setup -q

%build
mkdir -p build
cd build
cmake .. -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_PREFIX=/usr
make %{?_smp_mflags}

%install
rm -rf %{buildroot}
cd build
make install DESTDIR=%{buildroot}

%files
%defattr(-,root,root,-)
/usr/bin/%{name}
/usr/share/%{name}
/usr/share/applications/%{name}.desktop
/usr/share/icons/hicolor/*/apps/%{name}.png

%changelog
* Thu Oct 15 2026 smatkovi - 0.1.0-1
- First version: physics questions from eight Austrian school books (grades 6-12),
  German and English, built on BioQuiz 0.4.0
