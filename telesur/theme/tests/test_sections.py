# -*- coding: utf-8 -*-
import unittest2 as unittest

from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

from zope.component import getMultiAdapter
from Products.CMFCore.utils import getToolByName

from telesur.theme.testing import FUNCTIONAL_TESTING
from telesur.theme.testing import INTEGRATION_TESTING


class SectionsViewTest(unittest.TestCase):

    layer = INTEGRATION_TESTING

    def setUp(self):
        self.portal = self.layer['portal']
        self.request = self.layer['request']
        setRoles(self.portal, TEST_USER_ID, ['Manager'])

    def test_sectionview_number_of_elements(self):

        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setChainForPortalTypes(('collective.nitf.content',), 
                                     'simple_publication_workflow')
        
        self.portal.invokeFactory('collective.nitf.content', 'n1',
            genre='Current', section=u'Latinoamérica')
        n1 = self.portal['n1']

        ac = getMultiAdapter((n1, self.request), name="article-control")
        sectionview = getMultiAdapter((n1, self.request), name="section-view")

        #the result should be empty, because the nitf is not published
        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) != 1)
        self.failUnless(len(view_result['secondary']) != 1)

        #after publication, now we should have 1 new in outstanding
        workflowTool.doActionFor(n1, 'publish')
        view_result = sectionview.articles(section=u'Latinoamérica')        
        self.failUnless(len(view_result['outstanding']) == 1)        
        
        self.portal.invokeFactory('collective.nitf.content', 'n2',
            genre='Current', section=u'Latinoamérica')
        n2 = self.portal['n2']

        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) == 1)
        self.failUnless(len(view_result['secondary']) != 1)

        #after n1 and n2 publication, we should have the 2 news
        workflowTool.doActionFor(n2, 'publish')
        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) == 1)
        self.failUnless(len(view_result['secondary']) == 1)

        self.portal.invokeFactory('collective.nitf.content', 'n3',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n4',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n5',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n6',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n7',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n8',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n9',
            genre='Current', section=u'Latinoamérica')
        self.portal.invokeFactory('collective.nitf.content', 'n10',
            genre='Current', section=u'Latinoamérica')            
        n3 = self.portal['n3']
        n4 = self.portal['n4']
        n5 = self.portal['n5']
        n6 = self.portal['n6']
        n7 = self.portal['n7']        
        n8 = self.portal['n8']
        n9 = self.portal['n9']
        n10 = self.portal['n10']        
        workflowTool.doActionFor(n3, 'publish')
        workflowTool.doActionFor(n4, 'publish')
        workflowTool.doActionFor(n5, 'publish')
        workflowTool.doActionFor(n6, 'publish')
        workflowTool.doActionFor(n7, 'publish')
        workflowTool.doActionFor(n8, 'publish')
        workflowTool.doActionFor(n9, 'publish')
        workflowTool.doActionFor(n10, 'publish')        
        
        #9 news, 1 outstanding and 8 secondary
        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) == 1)
        self.failUnless(len(view_result['secondary']) == 8)

        #we mark the number 5 news like section news, and we check if is
        # in outstanding
        ac.mark_section(n5)
        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) == 1)
        self.failUnless(len(view_result['secondary']) == 8)
        self.failUnless(view_result['outstanding'][0].id == n5.id)

        #we mark the n10 like outstanding, and check the order
        ac.mark_section(n10)
        view_result = sectionview.articles(section=u'Latinoamérica')
        self.failUnless(len(view_result['outstanding']) == 1)
        self.failUnless(len(view_result['secondary']) == 8)
        self.failUnless(view_result['outstanding'][0].id == n10.id)
        self.failUnless(view_result['secondary'][0].id == n9.id)
        self.failUnless(view_result['secondary'][1].id == n8.id)
        self.failUnless(view_result['secondary'][2].id == n7.id)
        self.failUnless(view_result['secondary'][3].id == n6.id)
        self.failUnless(view_result['secondary'][4].id == n5.id)
        self.failUnless(view_result['secondary'][5].id == n4.id)
        self.failUnless(view_result['secondary'][6].id == n3.id)
        self.failUnless(view_result['secondary'][7].id == n2.id)

    def test_opinionview_number_of_elements(self):
        workflowTool = getToolByName(self.portal, 'portal_workflow')
        workflowTool.setChainForPortalTypes(('collective.nitf.content',), 
                                     'simple_publication_workflow')  

        self.portal.invokeFactory('collective.nitf.content', 'n1',
            genre='Opinion', section=u'Opinion')
        n1 = self.portal['n1']

        ac = getMultiAdapter((n1, self.request), name="article-control")
        opinionview = getMultiAdapter((n1, self.request), name="opinion-view")

        self.portal.invokeFactory('collective.nitf.content', 'n2',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n3',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n4',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n5',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n6',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n7',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n8',
            genre='Opinion', section=u'Opinion')
        self.portal.invokeFactory('collective.nitf.content', 'n9',
            genre='Opinion', section=u'Opinion')
        n2 = self.portal['n2']
        n3 = self.portal['n3']
        n4 = self.portal['n4']
        n5 = self.portal['n5']
        n6 = self.portal['n6']
        n7 = self.portal['n7']
        n8 = self.portal['n8']
        n9 = self.portal['n9']
        workflowTool.doActionFor(n1, 'publish')
        workflowTool.doActionFor(n2, 'publish')
        workflowTool.doActionFor(n3, 'publish')
        workflowTool.doActionFor(n4, 'publish')
        workflowTool.doActionFor(n5, 'publish')
        workflowTool.doActionFor(n6, 'publish')
        workflowTool.doActionFor(n7, 'publish')
        workflowTool.doActionFor(n8, 'publish')
        workflowTool.doActionFor(n9, 'publish')
                                           
        #in opinion view, only show the 8 permited elements in the articles key

        view_result = opinionview.articles(section=u'Opinion')
        self.failUnless(len(view_result['outstanding']) == 0)
        self.failUnless(len(view_result['secondary']) == 0)
        self.failUnless(len(view_result['articles']) == 8)
