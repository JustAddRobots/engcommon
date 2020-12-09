#!/usr/bin/env python3


def test_apihost(myini):
    assert isinstance(myini.apihost, str)


def test_buildhost(myini):
    assert isinstance(myini.buildhost, str)


def test_dockerhost(myini):
    assert isinstance(myini.dockerhost, str)


def test_jenkinshost(myini):
    assert isinstance(myini.jenkinshost, str)


def test_xhplconsole_url(myini):
    assert isinstance(myini.xhplconsole_url, str)


def test_kubeconfig(myini):
    assert isinstance(myini.kubeconfig, str)
