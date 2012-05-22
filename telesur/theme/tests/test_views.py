# -*- coding: utf-8 -*-

import unittest2 as unittest

from StringIO import StringIO

from zope.app.file.tests.test_image import zptlogo
from zope.component import getMultiAdapter
from zope.component import queryMultiAdapter
from zope.interface import directlyProvides

from plone.app.customerize import registration

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from Products.CMFCore.utils import getToolByName

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

    def test_nota_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('nota' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='nota')
        self.assertTrue(view is not None)

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
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('folder_summary_view' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='nota')
        self.assertTrue(view is not None)

    def test_schedule_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('schedule' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='schedule')
        self.assertTrue(view is not None)

    def test_live_signal_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('live-signal' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='live-signal')
        self.assertTrue(view is not None)

    def test_live_signal_backup_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('live-signal-backup' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='live-signal-backup')
        self.assertTrue(view is not None)

    def test_live_signal_alternative_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('live-signal-alternative' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='live-signal-alternative')
        self.assertTrue(view is not None)

    def test_donde_distribucion_view(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('donde-distribucion' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='donde-distribucion')
        self.assertTrue(view is not None)

    def test_more_articles_view_exists(self):
        registered = [v.name for v in registration.getViews(ITelesurLayer)]
        self.assertTrue('more-articles-view' in registered)

        view = queryMultiAdapter((self.n1, self.request), name='more-articles-view')
        self.assertTrue(view is not None)

    def test_viewlets_registered(self):
        # TODO: implement test
        pass

NEWS_LENGTH = 20
LIMIT = 8


class MoreArticlesTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']

        setRoles(self.portal, TEST_USER_ID, ['Manager'])

        directlyProvides(self.request, ITelesurLayer)
        self.workflowTool = getToolByName(self.portal, 'portal_workflow')
        self.workflowTool.setChainForPortalTypes(('collective.nitf.content',),
                                     'simple_publication_workflow')
        self.workflowTool.setChainForPortalTypes(('Topic',),
                                        'simple_publication_workflow')
        self.portal.invokeFactory('Topic', 'Deportes')
        self.section = self.portal['Deportes']
        section_crit = self.section.addCriterion('section', 'ATSimpleStringCriterion')
        section_crit.setValue('Deportes')
        self.workflowTool.doActionFor(self.section, 'publish')
        self.view = getMultiAdapter((self.section, self.request), name='more-articles-view')

    def test_more_articles_empty(self):
        self.view.update()
        self.assertEquals(len(self.view.articles), 0)

    def test_limit(self):
        self.create_articles()
        self.view.update()
        #8 que trae originalmente menos 1 que va para outstanding
        number = 0
        if NEWS_LENGTH > LIMIT:
            number = NEWS_LENGTH - LIMIT - 1
            if number > LIMIT:
                number = LIMIT
        self.assertEquals(len(self.view.articles), number)

    def test_pagination(self):
        self.create_articles()
        self.view.request['b_start'] = LIMIT * 2
        self.view.update()
        #LIMIT que trae originalmente menos 1 que va para outstanding
        number = 0
        if NEWS_LENGTH > LIMIT * 2:
            number = NEWS_LENGTH - LIMIT * 2 - 1
            if number > LIMIT:
                number = LIMIT
        self.assertEquals(len(self.view.articles), number)

    def create_articles(self):
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        for i in range(1, NEWS_LENGTH):
            self.portal.invokeFactory('collective.nitf.content', 'n%s' % i,
                genre='Current', section=u'Deportes')
            self.workflowTool.doActionFor(self.portal['n%s' % i], 'publish')


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
