# -*- coding: utf-8 -*-

import unittest2 as unittest

from StringIO import StringIO

from zope.app.file.tests.test_image import zptlogo
from zope.interface import directlyProvides

from plone.app.customerize import registration

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from telesur.theme.interfaces import ITelesurLayer
from telesur.theme.testing import INTEGRATION_TESTING


class BrowserLayerTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        directlyProvides(self.request, ITelesurLayer)

        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        self.portal.invokeFactory('Folder', 'test-folder')
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.folder = self.portal['test-folder']

        self.folder.invokeFactory('collective.nitf.content', 'n1')
        self.n1 = self.folder['n1']

    def getViewByName(self, context, name):
        try:
            return context.restrictedTraverse(name)
        except AttributeError:
            return None

    def test_views_registered(self):
        views = ['nota', 'folder_summary_view', 'schedule', 'live-signal']
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        # empty set only if all 'views' are 'registered'
        self.assertEquals(set(views) - set(registered), set([]))

    def test_nota(self):
        name = "@@nota"
        view = self.getViewByName(self.n1, name)
        self.failUnless(view, u"%s has no view %s" % (self.n1, name))

        self.assertEquals(view.has_images(), 0)
        self.assertEquals(view.has_files(), 0)
        self.assertEquals(view.has_links(), 0)

        self.n1.invokeFactory('Image', 'foo', title='Foo', description='FOO',
                              image=StringIO(zptlogo), filename='zpt.gif')
        self.n1.invokeFactory('File', 'bar', title='Bar', description='BAR',
                              image=StringIO(zptlogo), filename='zpt.gif')
        self.n1.invokeFactory('Link', 'baz', title='Baz', url='http://baz/')

        self.assertEquals(view.has_images(), 1)
        self.assertEquals(view.has_files(), 1)
        self.assertEquals(view.has_links(), 1)
        self.assertEquals(view.getImage()['id'], 'foo')

    def test_folder_summary_view(self):
        name = '@@folder_summary_view'
        try:
            self.n1.unrestrictedTraverse(name)
        except AttributeError:
            self.fail('%s has no view %s' % (self.n1, name))

    def test_schedule_view(self):
        name = '@@schedule'
        try:
            self.n1.unrestrictedTraverse(name)
        except AttributeError:
            self.fail('%s has no view %s' % (self.n1, name))

    def test_live_signal_view(self):
        name = '@@live-signal'
        try:
            self.n1.unrestrictedTraverse(name)
        except AttributeError:
            self.fail('%s has no view %s' % (self.n1, name))

    def test_viewlets_registered(self):
        # TODO: implement test
        pass


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
