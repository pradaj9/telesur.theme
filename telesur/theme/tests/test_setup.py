# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from telesur.theme.testing import INTEGRATION_TESTING

JS = [
    '++resource++telesur.theme/more-articles.js',
    ]


class InstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.qi = getattr(self.portal, 'portal_quickinstaller')

    def test_installed(self):
        self.assertTrue(self.qi.isProductInstalled('telesur.theme'))

    def test_dependencies_installed(self):
        DEPENDENCIES = ['collective.nitf']
        for p in DEPENDENCIES:
            self.assertTrue(self.qi.isProductInstalled(p),
                            '%s not installed' % p)

    def test_javascript_registry(self):
        """JS are properly registered at install time.
        """
        portal_javascripts = self.portal.portal_javascripts
        for js in JS:
            self.assertTrue(js in portal_javascripts.getResourceIds())


class UninstallTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        login(self.portal, TEST_USER_NAME)

    def test_uninstalled(self):
        qi = getattr(self.portal, 'portal_quickinstaller')
        qi.uninstallProducts(products=['telesur.theme'])
        self.assertFalse(qi.isProductInstalled('telesur.theme'))


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
