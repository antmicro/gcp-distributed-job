#!/usr/bin/env bash
set -e
set -u

mkdir -p renode_portable && cd renode_portable
curl -kL https://dl.antmicro.com/projects/renode/builds/renode-${RENODE_VERSION}.linux-portable.tar.gz | tar xz --strip 1
ln -s ../artifacts artifacts
echo `pwd` >> $GITHUB_PATH
pip3 install -r tests/requirements.txt
cd -
