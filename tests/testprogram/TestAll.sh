#! /bin/bash

make test-standalone &&
make test-standalone_nompi &&
make test-icon_standalone &&
make test-icon_testbed &&
make test-icon_standalone_legacy &&
make clean
