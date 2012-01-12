# -*- coding: utf-8 -*-

import unittest2 as unittest

from StringIO import StringIO

from zope.app.file.tests.test_image import zptlogo
from zope.interface import directlyProvides

from Products.CMFCore.utils import getToolByName
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

from telesur.theme.interfaces import ITelesurLayer
from telesur.theme.testing import FUNCTIONAL_TESTING
from telesur.theme.testing import browserLogin
from telesur.theme.testing import createObject
from telesur.theme.testing import setupTestContent


class BrowserLayerTest(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflow_tool = getToolByName(self.portal, 'portal_workflow')
        workflow_tool.setDefaultChain('one_state_workflow')
        workflow_tool.updateRoleMappings()
        setupTestContent(self)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        browserLogin(self.portal, self.browser)
        directlyProvides(self.request, ITelesurLayer)

    def test_nota(self):
        name = "/@@nota"
        self.browser.open(self.news1.absolute_url() + name )

    def test_folder_summary_view(self):
        name = "/@@folder_summary_view"
        self.browser.open(self.portal.absolute_url() + name )



def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
