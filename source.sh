#! /usr/bin/bash
# Generates all source tarballs
# Usage ./source.sh node_exporter-1.6.1
fedpkg prep
pushd $1
rm -rf vendor
go mod vendor
tar czvf ../vendor-$1.tar.gz vendor
popd

