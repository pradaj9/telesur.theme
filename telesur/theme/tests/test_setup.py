# -*- coding: utf-8 -*-

import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import login
from plone.app.testing import setRoles

from telesur.theme.testing import INTEGRATION_TESTING


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
