#!/bin/sh

if [ "$TRAVIS" = "true" ]; then
    pytest --cov=module tests

    coverage xml
    coveralls

    if [ "$TRAVIS_PULL_REQUEST" = "false" ]; then
        codeclimate-test-reporter --file .coverage
        python-codacy-coverage -r coverage.xml
    fi
else
    pytest tests
fi
