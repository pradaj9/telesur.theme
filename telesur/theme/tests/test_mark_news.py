# -*- coding: utf-8 -*-

import unittest2 as unittest

from zope.component import getMultiAdapter

from plone.testing.z2 import Browser
from telesur.theme.testing import browserLogin
from telesur.theme.testing import setupTestContent

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from telesur.theme.interfaces import IOutstandingArticle
from telesur.theme.interfaces import IPrimaryArticle
from telesur.theme.interfaces import ISecondaryArticle
from telesur.theme.interfaces import ISectionArticle

from telesur.theme.testing import INTEGRATION_TESTING
from telesur.theme.testing import FUNCTIONAL_TESTING


class MarkNewsTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_unmark_article(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_outstanding(n1)
        self.assertTrue(IOutstandingArticle.providedBy(n1))

        ac.unmark(n1)
        self.assertFalse(IOutstandingArticle.providedBy(n1))

        self.portal.invokeFactory('collective.nitf.content', 'n3')
        n3 = self.portal['n3']
        ac.mark_primary(n3)
        ac.mark_outstanding(n1)
        ac.unmark(n1)

        self.assertTrue(IOutstandingArticle.providedBy(n3))

        ac.mark_secondary(n2)
        ac.mark_primary(n1)

        ac.unmark(n3)

        self.assertFalse(IOutstandingArticle.providedBy(n3))
        self.assertFalse(IPrimaryArticle.providedBy(n3))
        self.assertFalse(ISecondaryArticle.providedBy(n3))

        self.portal.invokeFactory('collective.nitf.content', 'n4')
        n4 = self.portal['n4']

        ac.mark_secondary(n4)

        self.assertTrue(IOutstandingArticle.providedBy(n1))
        self.assertTrue(IPrimaryArticle.providedBy(n2))
        self.assertTrue(ISecondaryArticle.providedBy(n4))
        self.assertFalse(IPrimaryArticle.providedBy(n4))

    def test_mark_news_as_outstanding(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        self.assertFalse(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IOutstandingArticle.providedBy(n2))
        ac.mark_outstanding(n1)

        self.assertTrue(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IOutstandingArticle.providedBy(n2))
        ac.mark_outstanding(n2)

        self.assertFalse(IOutstandingArticle.providedBy(n1))
        self.assertTrue(IOutstandingArticle.providedBy(n2))

    def test_mark_news_as_primary(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        self.portal.invokeFactory('collective.nitf.content', 'n4')
        self.portal.invokeFactory('collective.nitf.content', 'n5')
        self.portal.invokeFactory('collective.nitf.content', 'n6')
        self.portal.invokeFactory('collective.nitf.content', 'n7')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        n4 = self.portal['n4']
        n5 = self.portal['n5']
        n6 = self.portal['n6']
        n7 = self.portal['n7']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n2))
        self.assertFalse(IPrimaryArticle.providedBy(n3))
        self.assertFalse(IPrimaryArticle.providedBy(n4))
        self.assertFalse(IPrimaryArticle.providedBy(n5))
        self.assertFalse(IPrimaryArticle.providedBy(n6))
        self.assertFalse(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n1)
        ac.mark_primary(n2)
        ac.mark_primary(n3)
        ac.mark_primary(n4)

        self.assertTrue(IPrimaryArticle.providedBy(n1))
        self.assertTrue(IPrimaryArticle.providedBy(n2))
        self.assertTrue(IPrimaryArticle.providedBy(n3))
        self.assertTrue(IPrimaryArticle.providedBy(n4))
        self.assertFalse(IPrimaryArticle.providedBy(n5))
        self.assertFalse(IPrimaryArticle.providedBy(n6))
        self.assertFalse(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n5)

        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertTrue(IPrimaryArticle.providedBy(n2))
        self.assertTrue(IPrimaryArticle.providedBy(n3))
        self.assertTrue(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertFalse(IPrimaryArticle.providedBy(n6))
        self.assertFalse(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n6)

        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n2))
        self.assertTrue(IPrimaryArticle.providedBy(n3))
        self.assertTrue(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertTrue(IPrimaryArticle.providedBy(n6))
        self.assertFalse(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n7)

        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n2))
        self.assertFalse(IPrimaryArticle.providedBy(n3))
        self.assertTrue(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertTrue(IPrimaryArticle.providedBy(n6))
        self.assertTrue(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n1)

        self.assertTrue(IPrimaryArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n2))
        self.assertFalse(IPrimaryArticle.providedBy(n3))
        self.assertFalse(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertTrue(IPrimaryArticle.providedBy(n6))
        self.assertTrue(IPrimaryArticle.providedBy(n7))

        ac.mark_primary(n2)

        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertTrue(IPrimaryArticle.providedBy(n2))
        self.assertFalse(IPrimaryArticle.providedBy(n3))
        self.assertFalse(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertTrue(IPrimaryArticle.providedBy(n6))
        self.assertTrue(IPrimaryArticle.providedBy(n7))

    def test_mark_news_as_secondary(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        self.assertFalse(ISecondaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n2))

        ac.mark_secondary(n1)

        self.assertTrue(ISecondaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n2))

        ac.mark_secondary(n2)

        self.assertTrue(ISecondaryArticle.providedBy(n1))
        self.assertTrue(ISecondaryArticle.providedBy(n2))

    def test_automatic_downgrade_marks(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        self.portal.invokeFactory('collective.nitf.content', 'n4')
        self.portal.invokeFactory('collective.nitf.content', 'n5')
        self.portal.invokeFactory('collective.nitf.content', 'n6')
        self.portal.invokeFactory('collective.nitf.content', 'n7')
        self.portal.invokeFactory('collective.nitf.content', 'n8')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        n4 = self.portal['n4']
        n5 = self.portal['n5']
        n6 = self.portal['n6']
        n7 = self.portal['n7']
        n8 = self.portal['n8']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_outstanding(n1)
        ac.mark_outstanding(n2)
        ac.mark_outstanding(n3)
        ac.mark_outstanding(n4)
        ac.mark_outstanding(n5)
        ac.mark_outstanding(n6)
        ac.mark_outstanding(n7)
        ac.mark_outstanding(n8)

        self.assertTrue(ISecondaryArticle.providedBy(n1))
        self.assertTrue(ISecondaryArticle.providedBy(n2))
        self.assertTrue(ISecondaryArticle.providedBy(n3))
        self.assertTrue(IPrimaryArticle.providedBy(n4))
        self.assertTrue(IPrimaryArticle.providedBy(n5))
        self.assertTrue(IPrimaryArticle.providedBy(n6))
        self.assertTrue(IPrimaryArticle.providedBy(n7))
        self.assertTrue(IOutstandingArticle.providedBy(n8))

    def test_marks_mutually_exclusive(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        n1 = self.portal['n1']

        self.assertFalse(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n1))

        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_outstanding(n1)

        self.assertTrue(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n1))

        ac.mark_primary(n1)

        self.assertFalse(IOutstandingArticle.providedBy(n1))
        self.assertTrue(IPrimaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n1))

        ac.mark_secondary(n1)

        self.assertFalse(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertTrue(ISecondaryArticle.providedBy(n1))

        ac.mark_outstanding(n1)

        self.assertTrue(IOutstandingArticle.providedBy(n1))
        self.assertFalse(IPrimaryArticle.providedBy(n1))
        self.assertFalse(ISecondaryArticle.providedBy(n1))

    def test_section_mark_can_live_with_others(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        n1 = self.portal['n1']

        ac = getMultiAdapter((n1, self.request), name="article-control")

        self.assertFalse(ISectionArticle.providedBy(n1))

        ac.mark_section(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))

        ac.mark_outstanding(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))

        ac.mark_primary(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))

        ac.mark_secondary(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))

    def test_only_one_section_mark_per_section(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        self.portal.invokeFactory('collective.nitf.content', 'n4')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        n4 = self.portal['n4']

        n1.section = 'section1'
        n1.reindexObject()
        n2.section = 'section1'
        n2.reindexObject()
        n3.section = 'section2'
        n3.reindexObject()
        n4.section = 'section3'
        n4.reindexObject()

        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_section(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))
        self.assertFalse(ISectionArticle.providedBy(n2))
        self.assertFalse(ISectionArticle.providedBy(n3))
        self.assertFalse(ISectionArticle.providedBy(n4))

        ac.mark_section(n2)

        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertFalse(ISectionArticle.providedBy(n3))
        self.assertFalse(ISectionArticle.providedBy(n4))

        ac.mark_section(n3)

        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertTrue(ISectionArticle.providedBy(n3))
        self.assertFalse(ISectionArticle.providedBy(n4))

        ac.mark_section(n4)

        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertTrue(ISectionArticle.providedBy(n3))
        self.assertTrue(ISectionArticle.providedBy(n4))

        ac.mark_section(n1)

        self.assertTrue(ISectionArticle.providedBy(n1))
        self.assertFalse(ISectionArticle.providedBy(n2))
        self.assertTrue(ISectionArticle.providedBy(n3))
        self.assertTrue(ISectionArticle.providedBy(n4))

    def test_changed_section_in_already_marked_section(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']

        n1.section = 'section1'
        n1.reindexObject()
        n2.section = 'section1'
        n2.reindexObject()
        n3.section = 'section2'
        n3.reindexObject()

        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_section(n1)
        self.assertTrue(ISectionArticle.providedBy(n1))
        self.assertFalse(ISectionArticle.providedBy(n2))
        self.assertFalse(ISectionArticle.providedBy(n3))

        ac.mark_section(n2)
        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertFalse(ISectionArticle.providedBy(n3))

        ac.mark_section(n3)
        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertTrue(ISectionArticle.providedBy(n3))

        n3.section = 'section1'
        n3.reindexObject()
        self.assertFalse(ISectionArticle.providedBy(n1))
        self.assertTrue(ISectionArticle.providedBy(n2))
        self.assertTrue(ISectionArticle.providedBy(n3))


class MarkNewsFunctionalTest(unittest.TestCase):

    layer = FUNCTIONAL_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])
        setupTestContent(self)
        setRoles(self.portal, TEST_USER_ID, ['Member'])
        self.browser = Browser(self.layer['app'])
        self.browser.handleErrors = False
        browserLogin(self.portal, self.browser)

    def test_actions_are_not_visible(self):
        #the article isn't published
        self.browser.open(self.news1.absolute_url())
        self.assertFalse('@@mark-outstanding-article' in self.browser.contents)
        self.assertFalse('@@mark-primary-article' in self.browser.contents)
        self.assertFalse('@@mark-secondary-article' in self.browser.contents)
        self.assertFalse('@@mark-section-article' in self.browser.contents)

    def test_actions_are_visible(self):
        #the article isn't published

        self.browser.open(self.news4.absolute_url())
        self.browser.getLink("Publish").click()
        self.assertTrue('@@mark-outstanding-article' in self.browser.contents)
        self.assertTrue('@@mark-primary-article' in self.browser.contents)
        self.assertTrue('@@mark-secondary-article' in self.browser.contents)
        self.assertTrue('@@mark-section-article' in self.browser.contents)

    def test_links_hide(self):
        self.browser.open(self.news1.absolute_url())
        self.browser.getLink("Publish").click()
        #XXX: Encontrar el encoding apropiado para "sección"
        self.browser.getLink("Marcar como destacado de secci�n").click()
        self.assertTrue('@@mark-outstanding-article' in self.browser.contents)
        self.assertTrue('@@mark-primary-article' in self.browser.contents)
        self.assertTrue('@@mark-secondary-article' in self.browser.contents)
        self.assertFalse('@@mark-section-article' in self.browser.contents)

        self.browser.getLink("Marcar como nota secundaria").click()
        self.assertTrue('@@mark-outstanding-article' in self.browser.contents)
        self.assertTrue('@@mark-primary-article' in self.browser.contents)
        self.assertFalse('@@mark-secondary-article' in self.browser.contents)
        self.assertFalse('@@mark-section-article' in self.browser.contents)

        self.browser.getLink("Marcar como nota principal").click()
        self.assertTrue('@@mark-outstanding-article' in self.browser.contents)
        self.assertFalse('@@mark-primary-article' in self.browser.contents)
        self.assertTrue('@@mark-secondary-article' in self.browser.contents)
        self.assertFalse('@@mark-section-article' in self.browser.contents)

        self.browser.getLink("Marcar como nota destacada").click()
        self.assertFalse('@@mark-outstanding-article' in self.browser.contents)
        self.assertTrue('@@mark-primary-article' in self.browser.contents)
        self.assertTrue('@@mark-secondary-article' in self.browser.contents)
        self.assertFalse('@@mark-section-article' in self.browser.contents)


def test_suite():
    return unittest.defaultTestLoader.loadTestsFromName(__name__)
