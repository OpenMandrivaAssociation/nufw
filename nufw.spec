# TODO 
#  initscript nuauth to revise ??

%define name	nufw
# (misc) do not upgrade tO 2.2 until 2008.0 is out, as
# everything changed and some others software were broken 
# please also warn me if something important need to be changed 
# ( like 2.0 => 2.2 )
%define version 2.0.22
%define release %mkrel 1

%define libname %mklibname nuclient 0

Name:		%{name}
Version:	%{version}
Release:	%{release}
Summary:	Authentication Firewall Suite for Linux
License:	GPL
Group:		Networking/Other
Source:		http://www.nufw.org/download/nufw/%{name}-%{version}.tar.bz2
Source1:    nufw.init
Source2:    nuauth.init
Source3:    nuauth.pam
Patch:      nufw.compile_2.0.22.diff
URL:		http://www.nufw.org/
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires: iptables
BuildRequires: postgresql-devel mysql-devel	gdbm-devel 
BuildRequires: gnutls-devel glib2-devel pam-devel libsasl2-devel 
BuildRequires: openldap-devel iptables-devel
BuildRequires: prelude-devel 
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}/buildroot

%description
NuFW is a firewall able to filter connection according to user uid or user 
software, meaning you can allows port 80 for only one user, whatever ip he 
uses, or only for konqueror.

NuFW performs an authentication of every single connection passing through the 
IP filter, by transparently requesting user's credentials before any filtering 
decision is taken. Practically, this means security policies can integrate with
the users directory, and bring the notion of user ID down to the IP layers.

%package utils
Summary:   Various utilities for Nufw administrators
Group:     Networking/Other
%description utils
This package contains various utilities :

  * nutop : a top-like utility to watch connection 

  * nutcpc : a console client to authenticate on nuauth gateway

  * nufw_dbm : a utility to mange list of user in a dbm file

  * nuaclgen : a perl script to add users to ldap

%package -n %libname
Summary:   Nuclient library
Group:     System/Libraries
%description -n %libname
Library needed by nufw for nuclient.

%package -n %libname-devel
Summary:   Nuclient development library
Group:     System/Libraries
Provides:  libnuclient-devel
Requires:  %libname = %version
%description -n %libname-devel
Development file of the nuclient library, used to compile
client accessing to nufw.

%package -n pam_nufw
Summary: Nufw client using pam credentials
Group:   Networking/Other

%description -n pam_nufw
pam_nufw is a PAM module able to integrate with the PAM stack. 
It reuse pam credentials to connect to nufw daemon, instead of requiring to 
start nutcpc by hand.

%package nutcpc
Summary: Nufw client
Group:   Networking/Other
%description nutcpc
Nutcpc is the command line client used to authenticate on a firewall using 
nufw.

%package  nuauth
Summary:   Nufw user database daemon
Group:     Networking/Other
Requires(post): rpm-helper
Requires(postun): rpm-helper
Requires(preun): rpm-helper
Requires(pre): rpm-helper
Requires: sasl-plug-login sasl-plug-plain
Obsoletes: nufw-nuauth-auth-plaintext nufw-nuauth-log-syslog nufw-nuauth-auth-system 
Provides:  nufw-nuauth-auth-plaintext nufw-nuauth-log-syslog nufw-nuauth-auth-system

%description   nuauth
NuFW is an authenticating gateway, which means that connections are 
authenticated before being forwarded through the gateway. Classical packet 
filtering systems disregard the identity of the user who may be attempting 
to access the network, instead caring only about the originating IP addresses. 

Nuauth lays on a user database, and an ACL system (which can reside in an LDAP 
directory, or XML/DBM solutions, etc. Nuauth receives requests from nufw, and 
auth packets from users' clients, and sends decision to the nufw daemon.

This package contains the main daemon.

%package nuauth-auth-dbm
Summary:   Module for nuauth providing dbm file user database
Group:     Networking/Other
%description  nuauth-auth-dbm
This package provides a module to use a dbm file as user database for nuauth.

%package nuauth-auth-ldap
Summary:   Module for nuauth providing ldap user database
Group:     Networking/Other
%description nuauth-auth-ldap
This package provides a module to use ldap as user database for nuauth.

%package nuauth-log-mysql
Summary:   Module for nuauth to log in Mysql database
Group:     Networking/Other
%description nuauth-log-mysql
This module allows you to log user activity in a mysql database.

%package nuauth-log-pgsql
Summary:   Module for nuauth to log in Postgresql database
Group:     Networking/Other
%description nuauth-log-pgsql
This module allows you to log user activity in a postgresql database.

%package nuauth-log-prelude
Summary:   Module for nuauth to log to Prelude IDS
Group:     Networking/Other
%description nuauth-log-prelude
This module allows you to log user activity to the Prelude IDS.

%prep
%setup -q
%patch0

perl -pi -e "s|postgresql|pgsql|" ./src/nuauth/modules/log_pgsql/Makefile*
# default config fix
perl -pi -e 's/^(nuauth_user_check_module="lib)dbm"/$1system"/' conf/nuauth.conf

# fix for lib64 policy
perl -pi -e 's|^(modulesdir\s*=\s*/)lib|$1%_lib|' ./src/clients/pam_nufw/Makefile* 
perl -pi -e 's|(\@modulesdir\s*=\s*/)lib|$1%_lib|' ./src/clients/pam_nufw/Makefile* 

%build
./autogen.sh
# there is no ident library
%configure --with-mysql-log --with-pgsql-log --with-utf8 \
           --with-ldap --with-system-auth --with-gdbm --with-user-mark \
           --with-prelude-log --sysconfdir=%{_sysconfdir}/nufw/ --localstatedir=%_var  
make

%install
rm -rf $RPM_BUILD_ROOT
%makeinstall_std

cp scripts/nuaclgen $RPM_BUILD_ROOT/%{_bindir}
cp scripts/nutop    $RPM_BUILD_ROOT/%{_bindir}

mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/nufw
cp conf/{nutop,nuauth,nuaclgen}.conf  $RPM_BUILD_ROOT/%{_sysconfdir}/nufw
cp conf/{acls.nufw,users-gdbm.nufw,periods.xml} $RPM_BUILD_ROOT/%{_sysconfdir}/nufw
cp -R conf/certs/* $RPM_BUILD_ROOT/%{_sysconfdir}/nufw
cp conf/users-plaintext.nufw $RPM_BUILD_ROOT/%{_sysconfdir}/nufw/users.nufw

mkdir -p $RPM_BUILD_ROOT/%{_localstatedir}/nuauth
mkdir -p $RPM_BUILD_ROOT/var/run/nuauth
# clean useless files
rm -f $RPM_BUILD_ROOT/%{_libdir}/nuauth/modules/*.{a,la}
rm -f $RPM_BUILD_ROOT/%{_lib}/security/*{a,la}

mkdir -p $RPM_BUILD_ROOT/%_initrddir/
install -m755 %SOURCE1 $RPM_BUILD_ROOT/%_initrddir/nufw
install -m755 %SOURCE2  $RPM_BUILD_ROOT/%_initrddir/nuauth
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/
cat > $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/nufw << EOF
# daemon verbosity
#VERBOSITY="vv"

# address where nufw listen ( -L )
#LISTEN_ADDRESS="127.0.0.1"

# default port -l
#LISTEN_UDP_PORT="4129"

# nuauth address ( -d )
#NUAUTH_ADDRESS="127.0.0.1"

# nuauth port ( -p )
#NUAUTH_UDP_PORT=4128

# Firewall timeout ( -t )
#FW_TIMEOUT=15

# Track size ( -T )
#TRACK_SIZE=1000


EOF

mkdir $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/
cp %SOURCE3 $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/nuauth

# (misc) zeck request for corporate server 4
%if %mdkversion < 200700 
perl -pi -e "s/include\s*system-auth/required  pam_stack.so service=system-auth/g" $RPM_BUILD_ROOT/%{_sysconfdir}/pam.d/nuauth
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n %{libname} -p /sbin/ldconfig
%postun -n %{libname} -p /sbin/ldconfig

%post 
%_post_service nufw

%preun 
%_preun_service nufw

# nuauth
%pre nuauth
%_pre_useradd nuauth %{_localstatedir}/nuauth /bin/false

%post nuauth
%_post_service nuauth

%postun nuauth
%_postun_userdel nuauth

%preun nuauth
%_preun_service nuauth

%files
%defattr(-, root, root)
%doc AUTHORS ChangeLog NEWS README TODO
%doc doc
%{_sbindir}/nufw
%{_mandir}/man8/nufw.8*
%config(noreplace) %{_initrddir}/nufw
%config(noreplace) %{_sysconfdir}/sysconfig/nufw
%dir %{_sysconfdir}/nufw/

%files utils
%defattr(-, root, root)
%{_bindir}/nuaclgen
%{_bindir}/nutop
%{_bindir}/nufw_dbm
%{_mandir}/man8/nuaclgen.8*
%{_mandir}/man8/nutop.8*
%{_mandir}/man8/nufw_dbm.8*
%config(noreplace) %{_sysconfdir}/nufw/nutop.conf
%config(noreplace) %{_sysconfdir}/nufw/nuaclgen.conf
%dir %{_sysconfdir}/nufw/

%files -n %libname
%defattr(-, root, root)
%{_libdir}/libnuclient.so.*

%files -n %libname-devel
%defattr(-, root, root)
%{_libdir}/libnuclient.a
%{_libdir}/libnuclient.la
%{_libdir}/libnuclient.so
%{_includedir}/*
%{_mandir}/man3/libnuclient.3*

%files -n pam_nufw
%defattr(-, root, root)
%doc doc/README.pam_nufw
/%{_lib}/security/pam_nufw.so


%files nuauth-auth-dbm
%defattr(-, root, root)
%{_libdir}/nuauth/modules/libdbm.so*
%config(noreplace) %{_sysconfdir}/nufw/users-gdbm.nufw

%files nuauth-auth-ldap
%defattr(-, root, root)
%doc conf/acls.schema
%{_libdir}/nuauth/modules/libldap.so*

%files nuauth-log-mysql
%defattr(-, root, root)
%doc conf/nulog*mysql.dump
%{_libdir}/nuauth/modules/libmysql.so*

%files nuauth-log-pgsql
%defattr(-, root, root)
%doc conf/nulog*pgsql.dump
%{_libdir}/nuauth/modules/libpgsql.so*

%files nuauth-log-prelude
%defattr(-, root, root)
%{_libdir}/nuauth/modules/libnuprelude.so*

%files nuauth
%defattr(-, root, root)
%{_sbindir}/nuauth
%{_mandir}/man8/nuauth.8*
%{_localstatedir}/nuauth
%dir /var/run/nuauth/
%config(noreplace) %{_initrddir}/nuauth
%config(noreplace) %{_sysconfdir}/%{name}/nuauth.conf
%config(noreplace) %{_sysconfdir}/%{name}/periods.xml
%config(noreplace) %{_sysconfdir}/%{name}/users.nufw
%config(noreplace) %{_sysconfdir}/%{name}/acls.nufw
%config(noreplace) %{_sysconfdir}/%{name}/*pem
%config(noreplace) %{_sysconfdir}/pam.d/nuauth
%dir %{_sysconfdir}/%{name}/
%{_libdir}/nuauth/modules/libsyslog.so*
%{_libdir}/nuauth/modules/libplaintext.so*
%{_libdir}/nuauth/modules/libsystem.so*
%{_libdir}/nuauth/modules/libscript.so*
%{_libdir}/nuauth/modules/libx509_std.so*
%{_libdir}/nuauth/modules/libxml_defs.so*
%{_libdir}/nuauth/modules/libipauth_guest.so*

%files nutcpc
%defattr(-, root, root)
%{_bindir}/nutcpc
%{_mandir}/man1/nutcpc.1*