#!/bin/bash
set -e

OAREPO_VERSION=${OAREPO_VERSION:-11}
OAREPO_VERSION_MAX=$((OAREPO_VERSION+1))

MODEL="thesis"
MODEL_VENV=".model_venv"
CODE_TEST_DIR="tests"
BUILD_TEST_DIR="tests"

if test ! -d $BUILD_TEST_DIR; then
  mkdir $BUILD_TEST_DIR
fi

if test -d $BUILD_TEST_DIR/$MODEL; then
  rm -rf $MODEL
fi

if test -d $MODEL_VENV; then
	rm -rf $MODEL_VENV
fi

oarepo-compile-model ./$CODE_TEST_DIR/$MODEL.yaml --output-directory ./$BUILD_TEST_DIR/$MODEL -vvv

python3 -m venv $MODEL_VENV
. $MODEL_VENV/bin/activate
pip install -U setuptools pip wheel
pip install "oarepo>=$OAREPO_VERSION,<$OAREPO_VERSION_MAX"
pip install "./$BUILD_TEST_DIR/$MODEL[tests]"
pip install .
pip install oarepo-ui

pytest $BUILD_TEST_DIR/test_requests
pytest $BUILD_TEST_DIR/test_ui