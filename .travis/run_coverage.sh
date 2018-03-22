#!/bin/sh

if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    coverage xml
    codeclimate-test-reporter --file .coverage
    python-codacy-coverage -r coverage.xml
fi
