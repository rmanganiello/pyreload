#!/bin/sh

coverage xml
coveralls

if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
    codeclimate-test-reporter --file .coverage
    python-codacy-coverage -r coverage.xml
fi
