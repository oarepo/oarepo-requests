#!/bin/bash
set -e

OAREPO_VERSION=${OAREPO_VERSION:-11}

MODEL="thesis"

BUILDER_VENV=.venv-builder
BUILD_TEST_DIR="tests"
CODE_TEST_DIR="tests"

if test -d $BUILDER_VENV ; then
	rm -rf $BUILDER_VENV
fi

python3 -m venv $BUILDER_VENV
. $BUILDER_VENV/bin/activate
pip install -U setuptools pip wheel
pip install -U oarepo-model-builder-tests oarepo-model-builder-requests oarepo-model-builder-drafts

if test -d ./$BUILD_TEST_DIR/$MODEL; then
  rm -rf ./$BUILD_TEST_DIR/$MODEL
fi

oarepo-compile-model ./$CODE_TEST_DIR/$MODEL.yaml --output-directory ./$BUILD_TEST_DIR/$MODEL -vvv

MODEL_VENV=".venv-tests"

if test -d $MODEL_VENV; then
	rm -rf $MODEL_VENV
fi
python3 -m venv $MODEL_VENV
. $MODEL_VENV/bin/activate
pip install -U setuptools pip wheel
pip install "oarepo[tests]==$OAREPO_VERSION.*"
pip install -e "./$BUILD_TEST_DIR/${MODEL}"
pip install oarepo-ui
pip install -e .

pytest $BUILD_TEST_DIR/test_requests
pytest $BUILD_TEST_DIR/test_ui