# -*- coding: utf-8 -*-

import unittest2 as unittest

from zExceptions import NotFound

from zope.component import getUtility

from Products.CMFCore.utils import getToolByName

from plone.registry.interfaces import IRegistry
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles
from plone.testing.z2 import Browser

from collective.nitf.controlpanel import INITFSettings
from collective.routes import addRoute
from collective.routes import getRouteNames
from collective.routes.controlpanel import IRoutesSettings

from telesur.theme.testing import FUNCTIONAL_TESTING
from telesur.theme.testing import browserLogin
from telesur.theme.testing import setupTestContent


class RoutesBrowserTest(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        self.nitfConfig()
        addRoute(u'Fecha',
                '/{effective:year}/{effective:month}/{effective:day}',
                defaultQuery={'portal_type': 'collective.nitf.content',
                    'review_state': 'published'})
        self.activateRoutes()
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        workflow_tool = getToolByName(self.portal, 'portal_workflow')
        workflow_tool.setDefaultChain('one_state_workflow')
        workflow_tool.updateRoleMappings()
        setupTestContent(self)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        browserLogin(self.portal, self.browser)

    def nitfConfig(self):
        registry = getUtility(IRegistry)
        nitf_settings = registry.forInterface(INITFSettings)
        nitf_settings.sections = set([u'General', u'Avances'])

    def activateRoutes(self):
        registry = getUtility(IRegistry)
        routes_settings = registry.forInterface(IRoutesSettings)
        routes_settings.routes = set([u'Fecha'])

    def test_routes(self):
        routes = getRouteNames()
        self.failUnless(u'Fecha' in routes)

    def test_fechas_no_results(self):
        fecha_url = self.portal.absolute_url() + '/2010'
        with self.assertRaises(NotFound):
            self.browser.open(fecha_url)

    def test_fechas_with_results(self):
        self.browser.open(self.portal.absolute_url() + '/2011')
        self.assertIn('News Test 1', self.browser.contents)
        self.assertIn('News Test 2',  self.browser.contents)
        self.browser.open(self.portal.absolute_url() + '/2011/09')
        self.assertIn('News Test 1', self.browser.contents)
        self.browser.open(self.portal.absolute_url() + '/2011/09/11')
        self.assertIn('News Test 1', self.browser.contents)
        self.browser.open(self.portal.absolute_url() + '/2011/10')
        self.assertIn('News Test 2', self.browser.contents)
        self.browser.open(self.portal.absolute_url() + '/2011/10/31')
        self.assertIn('News Test 2', self.browser.contents)
