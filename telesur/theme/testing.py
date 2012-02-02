# -*- coding: utf-8 -*-

import transaction

from plone.app.testing import PloneSandboxLayer
from plone.app.testing import PLONE_FIXTURE
from plone.app.testing import TEST_USER_NAME
from plone.app.testing import TEST_USER_PASSWORD
from plone.app.testing import IntegrationTesting
from plone.app.testing import FunctionalTesting

from plone.testing import z2


class Fixture(PloneSandboxLayer):

    defaultBases = (PLONE_FIXTURE,)

    def setUpZope(self, app, configurationContext):
        # Load ZCML
        import collective.formwidget.relationfield
        self.loadZCML(package=collective.formwidget.relationfield)
        import telesur.api
        self.loadZCML(package=telesur.api)
        import collective.upload
        self.loadZCML(package=collective.upload)
        import telesur.theme
        self.loadZCML(package=telesur.theme)

        # Install product and call its initialize() function
        z2.installProduct(app, 'Products.CMFPlacefulWorkflow')

    def setUpPloneSite(self, portal):
        # Set default workflow chains for tests
        wf = getattr(portal, 'portal_workflow')
        types = ('Topic', )
        wf.setChainForPortalTypes(types, 'one_state_workflow')
        types = ('Folder', 'collective.nitf.content')
        wf.setChainForPortalTypes(types, 'simple_publication_workflow')

        # Install into Plone site using portal_setup
        self.applyProfile(portal, 'collective.nitf:default')
        self.applyProfile(portal, 'collective.routes:default')
        self.applyProfile(portal, 'telesur.api:default')
        self.applyProfile(portal, 'telesur.theme:default')
        
        #adding the workflow to the container content type
        types = ('Container', 'collective.nitf.content')
        wf.setChainForPortalTypes(types, 'simple_publication_workflow')


FIXTURE = Fixture()
INTEGRATION_TESTING = IntegrationTesting(
    bases=(FIXTURE,),
    name='telesur.theme:Integration',
    )
FUNCTIONAL_TESTING = FunctionalTesting(
    bases=(FIXTURE,),
    name='telesur.theme:Functional',
    )


def browserLogin(portal, browser, username=None, password=None):
    handleErrors = browser.handleErrors
    try:
        browser.handleErrors = False
        browser.open(portal.absolute_url() + '/login_form')
        if username is None:
            username = TEST_USER_NAME
        if password is None:
            password = TEST_USER_PASSWORD
        browser.getControl(name='__ac_name').value = username
        browser.getControl(name='__ac_password').value = password
        browser.getControl(name='submit').click()
    finally:
        browser.handleErrors = handleErrors


def createObject(context, _type, id, delete_first=False,
                 check_for_first=False, **kwargs):
    if delete_first and id in context.objectIds():
        context.manage_delObjects([id])
    if not check_for_first or id not in context.objectIds():
        return context[context.invokeFactory(_type, id, **kwargs)]

    return context[id]


def setupTestContent(test):
    createObject(test.portal, 'Folder', 'folder',
            title='News Folder')
    test.folder = test.portal['folder']
    createObject(test.folder, 'collective.nitf.content', 'news-1',
            title='News Test 1')
    test.news1 = test.folder['news-1']
    test.news1.section = u'General'
    test.news1.setEffectiveDate('2011/09/11')
    createObject(test.folder, 'collective.nitf.content', 'news-2',
            title='News Test 2')
    test.news2 = test.folder['news-2']
    test.news2.section = u'Avances'
    test.news2.setEffectiveDate('2011/10/31')
    createObject(test.folder, 'collective.nitf.content', 'news-3',
            title='News Test 3')
    test.news3 = test.folder['news-3']
    test.news3.section = u'Latinoamérica'
    test.news3.setEffectiveDate('2011/10/31')
    createObject(test.folder, 'collective.nitf.content', 'news-4',
            title='News Test 4')
    test.news4 = test.folder['news-4']
    test.news4.section = u'Latinoamérica'
    test.news4.setEffectiveDate('2011/11/30')
    
    test.news1.reindexObject()
    test.news2.reindexObject()
    test.news3.reindexObject()
    test.news4.reindexObject()
    transaction.commit()