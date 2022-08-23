#!/usr/bin/env bash
set -e
set -u
set -x

pip install west
west init zephyrproject

mkdir -p zephyr-sdk && cd zephyr-sdk
curl -kL https://dl.antmicro.com/projects/renode/zephyr-sdk-${ZEPHYR_SDK_VERSION}_linux-x86_64.tar.gz | tar xz --strip 1
./setup.sh -t all -h -c
cd -

cd zephyrproject/zephyr
git checkout ${ZEPHYR_COMMIT}
git apply ../../patches/zephyr/*.patch
pip install -r scripts/requirements.txt 1>>../../artifacts/build.log 2>&1
cd ..
for i in $(seq 1 5); do west update 1>>../artifacts/build.log 2>&1 && break || sleep 5; done
west espressif install 1>>../artifacts/build.log 2>&1
cd ..

tar cf zephyr.tar zephyrproject zephyr-sdk
