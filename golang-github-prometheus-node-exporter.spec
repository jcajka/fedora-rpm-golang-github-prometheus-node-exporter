# Generated by go2rpm 1.3
%bcond_without check
%bcond_without bundled
%global shortname prometheus-node-exporter
%global debug_package %{nil}

# https://github.com/prometheus/node_exporter
%global goipath         github.com/prometheus/node_exporter
Version:                1.7.0

%gometa

%global common_description %{expand:
Prometheus exporter for hardware and OS metrics exposed by *NIX kernels, written
in Go with pluggable metric collectors.}

%global golicenses      LICENSE NOTICE
%global godocs          docs examples CHANGELOG.md CODE_OF_CONDUCT.md\\\
                        CONTRIBUTING.md MAINTAINERS.md SECURITY.md README.md

Name:           %{goname}
#autorelease seems to be broken in COPR
Release:        1%{?dist}
Summary:        Exporter for machine metrics

# Upstream license specification: Apache-2.0
License:        Apache-2.0 AND MIT
URL:            %{gourl}
Source0:        %{gosource}
Source1:        %{shortname}.sysusers
Source2:        %{shortname}.service
Source3:        %{shortname}.conf
Source4:        %{shortname}.logrotate
Source20:       vendor-node_exporter-%{version}.tar.gz
# Replace defaults paths for config files
Patch0:         defaults-paths.patch

BuildRequires:  systemd-rpm-macros
%if %{without bundled}
BuildRequires:  golang(github.com/beevik/ntp)
BuildRequires:  golang(github.com/coreos/go-systemd/dbus)
BuildRequires:  golang(github.com/dennwc/btrfs)
BuildRequires:  golang(github.com/ema/qdisc)
BuildRequires:  golang(github.com/go-kit/log)
BuildRequires:  golang(github.com/go-kit/log/level)
BuildRequires:  golang(github.com/godbus/dbus)
BuildRequires:  golang(github.com/hashicorp/go-envparse)
BuildRequires:  golang(github.com/hodgesds/perf-utils)
BuildRequires:  golang(github.com/jsimonetti/rtnetlink)
BuildRequires:  golang(github.com/mattn/go-xmlrpc)
BuildRequires:  golang(github.com/mdlayher/ethtool)
BuildRequires:  golang(github.com/mdlayher/wifi)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/collectors)
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/promhttp)
BuildRequires:  golang(github.com/prometheus/client_model/go)
BuildRequires:  golang(github.com/prometheus/common/expfmt)
BuildRequires:  golang(github.com/prometheus/common/promlog)
BuildRequires:  golang(github.com/prometheus/common/promlog/flag)
BuildRequires:  golang(github.com/prometheus/common/version)
BuildRequires:  golang(github.com/prometheus/exporter-toolkit/web)
BuildRequires:  golang(github.com/prometheus/procfs)
BuildRequires:  golang(github.com/prometheus/procfs/bcache)
BuildRequires:  golang(github.com/prometheus/procfs/blockdevice)
BuildRequires:  golang(github.com/prometheus/procfs/btrfs)
BuildRequires:  golang(github.com/prometheus/procfs/nfs)
BuildRequires:  golang(github.com/prometheus/procfs/sysfs)
BuildRequires:  golang(github.com/prometheus/procfs/xfs)
BuildRequires:  golang(github.com/safchain/ethtool)
BuildRequires:  golang(github.com/soundcloud/go-runit/runit)
BuildRequires:  golang(golang.org/x/sys/unix)
BuildRequires:  golang(gopkg.in/alecthomas/kingpin.v2)
%endif

%if %{with check}
%if %{without bundled}
# Tests
BuildRequires:  golang(github.com/prometheus/client_golang/prometheus/testutil)
%endif
%endif

Requires(pre): shadow-utils

%description
%{common_description}

%gopkg

%prep
%goprep
%patch 0 -p1
%if %{with bundled}
/usr/lib/rpm/rpmuncompress -x %{SOURCE20}
%endif

%build
LDFLAGS="-X github.com/prometheus/common/version.Version=%{version}  \
         -X github.com/prometheus/common/version.Revision=%{release} \
         -X github.com/prometheus/common/version.Branch=tarball      \
         -X github.com/prometheus/common/version.BuildDate=$(date -u -d@$SOURCE_DATE_EPOCH +%%Y%%m%%d)"
go build -mod=vendor -buildmode pie -compiler gc '-tags=rpm_crashtraceback netgo builtinassets' -ldflags '$LDFLAGS -compressdwarf=false -linkmode=external -extldflags '\''-Wl,-z,relro -Wl,--as-needed  -Wl,-z,now -specs=/usr/lib/rpm/redhat/redhat-hardened-ld -specs=/usr/lib/rpm/redhat/redhat-annobin-cc1  -Wl,--build-id=sha1 -specs=/usr/lib/rpm/redhat/redhat-package-notes  '\''' -a -v -x -o %{gobuilddir}/bin/node_exporter %{goipath}

%install
%gopkginstall
install -m 0755 -vd                     %{buildroot}%{_bindir}
install -m 0755 -vp %{gobuilddir}/bin/* %{buildroot}%{_bindir}/
mv %{buildroot}%{_bindir}/node_exporter %{buildroot}%{_bindir}/%{shortname}
pushd %{buildroot}%{_bindir}
ln -s %{shortname} node_exporter
popd

install -Dpm0644 %{S:1} %{buildroot}%{_sysusersdir}/%{shortname}.conf
install -Dpm0644 %{S:2} %{buildroot}%{_unitdir}/%{shortname}.service
pushd %{buildroot}%{_unitdir}
ln -s %{shortname}.service node_exporter.service
popd
install -Dpm0644 %{S:3} %{buildroot}%{_sysconfdir}/default/%{shortname}
install -Dpm0644 example-rules.yml %{buildroot}%{_datadir}/prometheus/node-exporter/example-rules.yml
install -Dpm0644 %{S:4} %{buildroot}%{_sysconfdir}/logrotate.d/%{shortname}
mkdir -vp %{buildroot}%{_sharedstatedir}/prometheus/node-exporter

# Build man pages.
mkdir -vp %{buildroot}/%{_mandir}/man1/
%{buildroot}%{_bindir}/%{shortname} --help-man > \
    %{buildroot}/%{_mandir}/man1/%{shortname}.1
sed -i '/^  /d; /^.SH "NAME"/,+1c.SH "NAME"\nprometheus-node-exporter \\- The Prometheus Node-Exporter' \
    %{buildroot}/%{_mandir}/man1/%{shortname}.1

%if %{with check}
%check
%gocheck -d collector
%endif

%pre
%sysusers_create_compat %{SOURCE1}

%post
%systemd_post %{shortname}.service

%preun
%systemd_preun %{shortname}.service

%postun
%systemd_postun_with_restart %{shortname}.service

%files
%license LICENSE NOTICE
%doc docs examples CHANGELOG.md CODE_OF_CONDUCT.md CONTRIBUTING.md
%doc MAINTAINERS.md SECURITY.md README.md
%{_bindir}/*
%config(noreplace) %{_sysconfdir}/default/%{shortname}
%config(noreplace) %{_sysconfdir}/logrotate.d/%{shortname}
%{_sysusersdir}/%{shortname}.conf
%{_unitdir}/%{shortname}.service
%{_unitdir}/node_exporter.service
%{_mandir}/man1/%{shortname}.1*
%{_datadir}/prometheus/node-exporter/example-rules.yml
%dir %attr(0755,prometheus,prometheus) %{_sharedstatedir}/prometheus
%dir %attr(0755,prometheus,prometheus) %{_sharedstatedir}/prometheus/node-exporter

%gopkgfiles

%changelog
%autochangelog
