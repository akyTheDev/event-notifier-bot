#!/usr/bin/env bash

set -e
set -x

export $(grep -v '^#' .env.test | xargs)

poetry run python -m coverage run -m pytest -lv ${ARGS}
poetry run python -m coverage report -m
