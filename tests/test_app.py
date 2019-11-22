import pytest

from flask import Flask


@pytest.mark.usefixtures('app')
def test_app(app):
    assert app is not None
    assert isinstance(app, Flask)


@pytest.mark.usefixtures('app')
def test_app_environment(app):
    assert app.config['TESTING']


@pytest.mark.usefixtures('app_runner')
def test_cli_help(app_runner):
    result = app_runner.invoke(args=['--help'])
    assert 'Show this message and exit.' in result.output
