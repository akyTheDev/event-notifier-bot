#!/usr/bin/env bash

set -e
set -x

poetry run ruff format
poetry run ruff check --fix
