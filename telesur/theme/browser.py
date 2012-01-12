# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from five import grok

from zope.component import getMultiAdapter

from zope.interface import Interface
from zope.publisher.interfaces import NotFound

from Products.CMFCore.interfaces import IFolderish

from collective.nitf.browser import View
from collective.nitf.content import INITF
from collective.routes.interfaces import IFragmentContext
from collective.routes.interfaces import IWrappedBrainsContext
from collective.routes.interfaces import IWrappedObjectContext
from collective.routes import getObject

from telesur.theme.interfaces import ITelesurLayer
from telesur.theme.interfaces import IOutstandingArticle
from telesur.theme.interfaces import IPrimaryArticle
from telesur.theme.interfaces import ISecondaryArticle
from telesur.theme.interfaces import ISectionArticle

from Acquisition import aq_inner
from zope.interface import alsoProvides, noLongerProvides

from Products.statusmessages.interfaces import IStatusMessage
from Products.CMFCore.utils import getToolByName

grok.templatedir("templates")


# TODO: refactorizar, esta vista se debe llamar simplemente View para
# sobreescribir la vista por defecto
class NITF_View(View):
    """El funcionamiento por defecto de la vista del NITF es el siguiente:
    - un artículo puede contener fotos, enlaces y archivos
    - las fotos se muestran como galería; los otros elementos como contenido

    El funcionamiento de esta vista en el caso de teleSUR es diferente:
    - un artículo puede contener fotos, enlaces y archivos
    - las fotos se muestran como galería
    - si un enlace corresponde a un video del servidor de multimedia, el
      enlace ser reemplaza por un player que muestra el video; cualquier otro
      enlace se muestra como contenido
    - como elemento principal se muestra el video o, en su defecto, la
      galería de fotos
    """
    grok.context(INITF)
    grok.name("nota")
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")


class Folder_Summary_View(grok.View):
    grok.context(IFolderish)
    grok.name("folder_summary_view")
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")


class Routes_Folder_Summary_View(Folder_Summary_View):
    grok.context(IWrappedBrainsContext)
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")


class FragmentView(grok.View):
    grok.context(IFragmentContext)
    grok.name("view")
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")

    def render(self):
        route = self.context.route
        wrapped = getObject(route, self.context, self.request)

        if IWrappedBrainsContext.providedBy(wrapped):
            wrapped.Title = lambda: u"TeleSUR"
            view = wrapped.restrictedTraverse('folder_summary_view')
        elif IWrappedObjectContext.providedBy(wrapped):
            layout = wrapped.obj.getLayout()
            view = wrapped.restrictedTraverse(layout)
        else:
            raise NotFound
        return view()


class Opinion(grok.View):
    grok.context(INITF)
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')


class MarkOutstandingArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-outstanding-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        self.mark(self.context)
        IStatusMessage(self.request).addStatusMessage("Elemento marcado como destacado para portada.", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def mark(self, element):
        iface = IOutstandingArticle
        iface_to_remove = [IPrimaryArticle, ISecondaryArticle]

        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=iface.__module__+'.'+iface.__name__)

        if existing:
            elem = existing[0].getObject()
            mark_primary = getMultiAdapter((self.context, self.request),
                                           name="mark-primary-article")
            mark_primary.mark(elem)

        context = aq_inner(element)
        alsoProvides(context, iface)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)
            
        context.reindexObject(idxs=['object_provides'])

    def render(self):
        return "mark-outstanding-article"


class MarkPrimaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-primary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        self.mark(self.context)
        IStatusMessage(self.request).addStatusMessage("Elemento marcado como principal para portada", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def mark(self, element):
        iface = IPrimaryArticle
        iface_to_remove = [IOutstandingArticle, ISecondaryArticle]

        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=iface.__module__+'.'+iface.__name__,
                           sort_on='modified')

        if len(existing) > 4:
            elem = existing[0].getObject()
            mark_secondary = getMultiAdapter((self.context, self.request),
                                             name="mark-secondary-article")
            mark_secondary.mark(elem)

        context = aq_inner(element)
        alsoProvides(context, iface)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)
            
        context.reindexObject(idxs=['object_provides'])

    def render(self):
        return "mark-primary-article"


class MarkSecondaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-secondary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        self.mark(self.context)
        IStatusMessage(self.request).addStatusMessage("Elemento marcado como secundario para portada", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)
        
    def mark(self, element):
        iface = ISecondaryArticle
        iface_to_remove = [IOutstandingArticle, IPrimaryArticle]

        context = aq_inner(element)
        alsoProvides(context, iface)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)
            
        context.reindexObject(idxs=['object_provides'])

    def render(self):
        return "mark-secondary-article"


class MarkSectionArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-section-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        self.mark(self.context)
        IStatusMessage(self.request).addStatusMessage("Elemento marcado como destacado de sección", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def mark(self, element):
        iface = ISectionArticle

        catalog = getToolByName(self.context, 'portal_catalog')
        # Buscar *solo* para esta sección
        existing = catalog(object_provides=iface.__module__+'.'+iface.__name__)

        if existing:
            elem = existing[0].getObject()
            context = aq_inner(elem)
            noLongerProvides(context, iface)
            context.reindexObject(idxs=['object_provides'])
            
        context = aq_inner(element)

        alsoProvides(context, iface)
        context.reindexObject(idxs=['object_provides'])

    def render(self):
        return "mark-secondary-article"


class ArticleControl(grok.View):
    grok.context(INITF)
    grok.name("article-control")
    grok.require("cmf.ModifyPortalContent")

    security = ClassSecurityInfo()

    security.declarePublic('can_be_promoted')
    def can_be_promoted(self, atype):
        ifaces = {
                   'outstanding' : IOutstandingArticle,
                   'primary' : IPrimaryArticle,
                   'secondary' : ISecondaryArticle,
                   'section' : ISectionArticle,
                  }

        return not ifaces[atype].providedBy(self.context)

    def render(self):
        return self

