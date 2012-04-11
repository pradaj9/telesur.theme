# -*- coding: utf-8 -*-

import unittest2 as unittest


from plone.testing.z2 import Browser

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from plone.app.uuid.utils import uuidToObject

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName


from telesur.theme.interfaces import IPrimaryArticle
from telesur.theme.interfaces import ISecondaryArticle

from telesur.theme.testing import INTEGRATION_TESTING


class DandDOrderNews(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_order_primary(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_primary(n1)
        ac.mark_primary(n2)
        ac.mark_primary(n3)

        elements = [x[0] for x in self.get_primary()]

        #change the order, first moved to the end
        home_set_order = getMultiAdapter((n1, self.request), name="home-set-order")
        home_set_order.render(elements[0], 2, 'primary')

        ordered_elements = [x[0] for x in self.get_primary()]

        self.assertTrue(ordered_elements[2] == elements[0])
        self.assertTrue(ordered_elements[0] == elements[1])
        self.assertTrue(ordered_elements[1] == elements[2])

        #create a new element, should be first, and the rest exactly the same
        self.portal.invokeFactory('collective.nitf.content', 'n4')
        n4 = self.portal['n4']
        ac.mark_primary(n4)
        elements2 = [x[0] for x in self.get_primary()]

        self.assertFalse(elements2[0] in ordered_elements)
        self.assertTrue(ordered_elements[0] == elements2[1])
        self.assertTrue(ordered_elements[1] == elements2[2])
        self.assertTrue(ordered_elements[2] == elements2[3])

    def test_order_secondary(self):
        self.portal.invokeFactory('collective.nitf.content', 'n1')
        self.portal.invokeFactory('collective.nitf.content', 'n2')
        self.portal.invokeFactory('collective.nitf.content', 'n3')
        n1 = self.portal['n1']
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        ac = getMultiAdapter((n1, self.request), name="article-control")

        ac.mark_secondary(n1)
        ac.mark_secondary(n2)
        ac.mark_secondary(n3)

        elements = [x[0] for x in self.get_secondary()]

        #change the order, first moved to the end
        home_set_order = getMultiAdapter((n1, self.request), name="home-set-order")
        home_set_order.render(elements[0], 2, 'secondary')

        ordered_elements = [x[0] for x in self.get_secondary()]

        self.assertTrue(ordered_elements[2] == elements[0])
        self.assertTrue(ordered_elements[0] == elements[1])
        self.assertTrue(ordered_elements[1] == elements[2])

        #create a new element, should be first, and the rest exactly the same
        self.portal.invokeFactory('collective.nitf.content', 'n4')
        n4 = self.portal['n4']
        ac.mark_secondary(n4)
        elements2 = [x[0] for x in self.get_secondary()]

        self.assertFalse(elements2[0] in ordered_elements)
        self.assertTrue(ordered_elements[0] == elements2[1])
        self.assertTrue(ordered_elements[1] == elements2[2])
        self.assertTrue(ordered_elements[2] == elements2[3])

    def get_primary(self):
        order = getMultiAdapter((self.portal, self.request), name='home-view-order')
        catalog = getToolByName(self.portal, 'portal_catalog')
        elements = catalog(object_provides=IPrimaryArticle.__identifier__,
                           sort_on='effective', sort_order='reverse')

        primary = order.primary_order(elements)
        elements = [(uuid, uuidToObject(uuid)) for uuid in primary]

        return elements

    def get_secondary(self):
        order = getMultiAdapter((self.portal, self.request), name='home-view-order')
        catalog = getToolByName(self.portal, 'portal_catalog')
        elements = catalog(object_provides=ISecondaryArticle.__identifier__,
                           sort_on='effective', sort_order='reverse')

        secondary = order.secondary_order(elements)
        elements = [(uuid, uuidToObject(uuid)) for uuid in secondary]

        return elements
