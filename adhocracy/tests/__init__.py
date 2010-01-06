"""Pylons application test package

This package assumes the Pylons environment is already loaded, such as
when this script is imported from the `nosetests --with-pylons=test.ini`
command.

This module initializes the application via ``websetup`` (`paster
setup-app`) and provides the base testing objects.
"""
from unittest import TestCase

from paste.deploy import loadapp
from paste.script.appinstall import SetupCommand
from pylons import config, url
from routes.util import URLGenerator
from webtest import TestApp

import pylons.test

import adhocracy.model as model
from testtools import *

__all__ = ['environ', 'url', 'TestController', 'WebTestController']

# Invoke websetup with the current config file
SetupCommand('setup-app').run([config['__file__']])

environ = {}

class TestController(TestCase):

    def __init__(self, *args, **kwargs):
        if pylons.test.pylonsapp:
            wsgiapp = pylons.test.pylonsapp
        else:
            wsgiapp = loadapp('config:%s' % config['__file__'])
        self.app = TestApp(wsgiapp)
        url._push_object(URLGenerator(config['routes.map'], environ))
        TestCase.__init__(self, *args, **kwargs)
        
class WebTestController(TestController):
        
    DEFAULT = model.Group.CODE_DEFAULT
    OBSERVER = model.Group.CODE_OBSERVER
    VOTER = model.Group.CODE_VOTER
    SUPERVISOR = model.Group.CODE_SUPERVISOR
        
    def prepare_app(self, anonymous=False, group_code=None, instance=True):
        self.app.extra_environ = dict()
        self.user = None
        if not anonymous:
            group = None
            if group_code: 
                group = model.Group.by_code(group_code)
            self.user = tt_make_user(instance_group=group)
            self.app.extra_environ['REMOTE_USER'] = str(self.user.user_name)
        if instance:
            self.app.extra_environ['HTTP_HOST'] = "test.test.lan"
        else:
            self.app.extra_environ['HTTP_HOST'] = "test.lan"
        
        
        