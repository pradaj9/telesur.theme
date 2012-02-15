# -*- coding: utf-8 -*-
import datetime
import DateTime

from Acquisition import aq_inner
from five import grok
from zope.interface import alsoProvides
from zope.interface import Interface
from zope.component import getMultiAdapter
from zope.security import checkPermission
from zope.app.component.hooks import getSite

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone.browser.navtree import NavtreeQueryBuilder

from plone.app.layout.navigation.navtree import buildFolderTree
from plone.app.layout.navigation.interfaces import INavtreeStrategy
from plone.app.layout.navigation.root import getNavigationRoot
from plone.app.layout.viewlets.interfaces import IDocumentActions
from plone.app.layout.viewlets.interfaces import IPortalHeader, IPortalFooter
from plone.app.portlets.portlets.navigation import Assignment

from collective.nitf.content import INITF
from telesur.theme.interfaces import ITelesurLayer
from telesur.theme.interfaces import ITelesurViewlet


grok.templatedir("viewlets")


class IExternalViewlet(Interface):
    """ A marker interface for viewlets for queries with external content"""


class TelesurSeccionViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name("telesur.theme.seccion_viewlets")


class TelesurVideoViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name("telesur.theme.video_viewlets")


class TelesurVideoBusquedaViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name("telesur.theme.video_busqueda_viewlets")


class TelesurVideoSeccionViewletManager(grok.ViewletManager):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name("telesur.theme.video_seccion_viewlets")


class VideosMasVistosViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.masvistos")
    grok.require("zope2.View")
    grok.template("videos_masvistos_viewlet")
    grok.viewletmanager(TelesurVideoViewletManager)

alsoProvides(VideosMasVistosViewlet, IExternalViewlet)


class MasTitularesViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.mas_titulares")
    grok.require("zope2.View")
    grok.template("carousel_viewlet")
    grok.viewletmanager(TelesurSeccionViewletManager)

    def update(self):
        self.portal_api = getMultiAdapter((self.context, self.request),
                                           name=u"portal_api")

    def getSections(self, limit=3):
        return self.portal_api.get_first_of_sections(limit=limit)

alsoProvides(MasTitularesViewlet, ITelesurViewlet)


class Related_Contents_Telesur(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.related_contents")
    grok.require("zope2.View")
    grok.template("related_contents_telesur")
    grok.viewletmanager(TelesurVideoBusquedaViewletManager)

alsoProvides(Related_Contents_Telesur, ITelesurViewlet)


## Viewlets de INITF
class VideosRelacionarViewlet(grok.Viewlet):
    grok.context(INITF)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.related_videos")
    grok.require("zope2.View")
    grok.template("related_contents_telesur")
    grok.viewletmanager(IDocumentActions)

alsoProvides(VideosRelacionarViewlet, ITelesurViewlet)


class ContentButtonsViewlet(grok.Viewlet):
    grok.context(INITF)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.content_buttons")
    grok.require("zope2.View")
    grok.template("content_buttons")
    grok.viewletmanager(IDocumentActions)

    def _checkPermInFolder(self, perm, folder_id=None):
        portal = getToolByName(self.context, 'portal_url').getPortalObject()
        if folder_id:
            try:
                folder = portal[folder_id]
            except KeyError:
                folder = None
        else:
            folder = portal
        if folder:
            can_add = checkPermission(perm, folder)
        else:
            can_add = False

        return can_add

    def canAddNews(self):
        can_add = self._checkPermInFolder('collective.nitf.AddNewsArticle',
                                          'articulos')
        return can_add

    def get_actions(self):
        actionIds = ['nota_destacada', 'nota_principal', 'nota_secundaria', 'nota_seccion']
        context_state = getMultiAdapter((self.context, self.request), name='plone_context_state')
        editActions = context_state.actions('object_buttons')
        editActionsIds = {}
        actions = []
        review_state = None
        workflows = self.context.portal_workflow.getWorkflowsFor(self.context)
        if workflows:
            wf_def = workflows[0]
            review_state = self.context.portal_workflow.getStatusOf(
            wf_def.getId(), self.context)['review_state']
        if review_state == "published":
            for action in editActions:
                editActionsIds[action['id']] = action
            for index, actionId in enumerate(actionIds):
                if actionId in editActionsIds.keys():
                    actions.append(editActionsIds[actionId])
                else:
                    action = self.context.portal_actions.object_buttons[actionId]
                    actionDic = {'id': actionId, 'title': action.title,
                        'available': False, 'url': None}
                    actions.append(actionDic)
        return actions

    def get_addable_contents(self):
        contents = []
        contents.append({'id': 'Video',
                                'title': 'Video',
                                'id-tag': "notas-add-video",
                                'url': ""})
        contents.append({'id': 'Images',
                                'title': 'Imagenes y Archivos',
                                'id-tag': "notas-add-image-files",
                                'url': "./@@media_uploader"})
        return contents

    def update(self):
        #get the actions
        if self._checkPermInFolder('cmf.ModifyPortalContent'):
            self.actions = self.get_actions()
        else:
            self.actions = []
        #get the contenttypes info
        if self.canAddNews():
            self.contents = self.get_addable_contents()
        else:
            self.contents = []


alsoProvides(VideosRelacionarViewlet, ITelesurViewlet)


class VideosPorSeccionViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.videosporseccion")
    grok.require("zope2.View")
    grok.template("videos_porseccion_viewlet")
    grok.viewletmanager(TelesurVideoSeccionViewletManager)

alsoProvides(VideosPorSeccionViewlet, ITelesurViewlet)


class DropdownQueryBuilder(NavtreeQueryBuilder):
    """Build a folder tree query suitable for a dropdownmenu"""

    def __init__(self, context):
        NavtreeQueryBuilder.__init__(self, context)
        #dropdown_properties = getToolByName(context,
        #                             'portal_properties').dropdown_properties
        #dropdown_depth = dropdown_properties.getProperty('dropdown_depth', 3)
        portal_path = context.portal_url.getPortalObject().getPhysicalPath()
        portal_len = len(portal_path)
        context_url = context.getPhysicalPath()
        self.query['path'] = {'query': '/'.join(context_url[:(portal_len + 1)]),
                              'navtree_start': 1,
                              'depth': 2}


class MobileNavigation(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.mobilenavigation")
    grok.require("zope2.View")
    grok.template("mobile_navigation")
    grok.viewletmanager(IPortalFooter)

    def update(self):
        self.result = []
        sections = ['noticias', 'opinion']
        self.navroot_path = getNavigationRoot(self.context)
        self.data = Assignment(root=self.navroot_path)
        self.year = datetime.date.today().strftime("%Y")
        for section in sections:
            catalog_news = self.context.portal_catalog({'portal_type': 'Topic',
                                'path': '%s/%s/' % (self.navroot_path, section)})
            if catalog_news:
                tab = catalog_news[0].getObject()
                strategy = getMultiAdapter((tab, self.data), INavtreeStrategy)
                queryBuilder = DropdownQueryBuilder(tab)
                query = queryBuilder()

                if query['path']['query'] != self.navroot_path:
                    news_dict = buildFolderTree(tab, obj=tab, query=query,
                        strategy=strategy)
                    self.result += news_dict.get('children', [])
                else:
                    news_dict = {}

        for item in self.result:
            if self.context.getId() == item['id']:
                item['is_selected'] = True
            else:
                item['is_selected'] = False


class LiveSignalLinkViewlet(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.livesignal")
    grok.require("zope2.View")
    grok.template("live_signal")
    grok.viewletmanager(IPortalFooter)

    def update(self):
        site = getSite()
        self.url = ""
        if site and 'el-canal' in site.keys() and \
            'senal-en-vivo' in site['el-canal'].keys():
            self.url = site['el-canal']['senal-en-vivo'].absolute_url()


class SubSectionList(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.videosporseccion")
    grok.require("zope2.View")
    grok.template("sub_section_list")
    grok.viewletmanager(IPortalHeader)

    def update(self):
        self.navroot_path = getNavigationRoot(self.context)
        self.data = Assignment(root=self.navroot_path)

        #common.ViewletBase.update(self) # Get portal_state and portal_url
        tab = aq_inner(self.context)
        #portal = self.portal_state.portal()

        strategy = getMultiAdapter((tab, self.data), INavtreeStrategy)
        queryBuilder = DropdownQueryBuilder(tab)
        query = queryBuilder()

        if query['path']['query'] != self.navroot_path:
            self.data = buildFolderTree(tab, obj=tab, query=query, strategy=strategy)
        else:
            self.data = {}


class SiteDate(grok.Viewlet):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name(u"telesur.theme.sitedate")
    grok.require("zope2.View")
    grok.template("site_date")
    grok.viewletmanager(IPortalFooter)

    def update(self):
        weekdays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves',
                    'Viernes', 'Sábado']
        months = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio',
                  'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        weekday = DateTime.DateTime().strftime('%w')
        day = int(DateTime.DateTime().strftime('%d'))
        month = DateTime.DateTime().strftime('%m')
        year = DateTime.DateTime().strftime('%Y')
        w = int(weekday)
        m = int(month) - 1
        self.date = '%s %s de %s de %s' % (weekdays[w], day, months[m], year)
