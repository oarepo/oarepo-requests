#!/bin/bash
set -e
export PYTHONWARNINGS="ignore"
OAREPO_VERSION=${OAREPO_VERSION:-12}
PYTHON="${PYTHON:-python3.12}"

export PIP_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple
export UV_EXTRA_INDEX_URL=https://gitlab.cesnet.cz/api/v4/projects/1408/packages/pypi/simple
MODEL="thesis"

BUILDER_VENV=".venv-builder"
BUILD_TEST_DIR="test-repositories"
CODE_TEST_DIR="tests"

if test -d $BUILDER_VENV ; then
	rm -rf $BUILDER_VENV
fi
${PYTHON} -m venv $BUILDER_VENV
. $BUILDER_VENV/bin/activate
pip install -U setuptools pip wheel
pip install -U oarepo-model-builder \
               oarepo-model-builder-tests \
               oarepo-model-builder-requests \
               oarepo-model-builder-drafts \
               oarepo-model-builder-workflows \
               oarepo-model-builder-files \
               oarepo-model-builder-drafts-files

if test -d ./$BUILD_TEST_DIR/$MODEL; then
  rm -rf ./$BUILD_TEST_DIR/$MODEL
fi

oarepo-compile-model ./$CODE_TEST_DIR/$MODEL.yaml --output-directory ./$BUILD_TEST_DIR/$MODEL -vvv

MODEL_VENV=".venv-tests"

if test -d $MODEL_VENV; then
	rm -rf $MODEL_VENV
fi
"${PYTHON}" -m venv $MODEL_VENV
. $MODEL_VENV/bin/activate
pip install -U setuptools pip wheel
pip install "oarepo[tests,rdm]==$OAREPO_VERSION.*"
pip install -e "./$BUILD_TEST_DIR/${MODEL}"

# Check if we can import all the sources
find oarepo_requests -name '*.py' | grep -v '__init__.py' | sed 's/.py$//' | tr '/' '.' | sort -u | while read MODULE ; do
    echo "import $MODULE"
done | python

pip install -e ".[tests]"
pytest tests/test_requests -v -s
pytest tests/test_ui