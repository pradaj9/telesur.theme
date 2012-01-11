# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from five import grok

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
from telesur.theme.interfaces import IPrimaryArticle
from telesur.theme.interfaces import ISecondaryArticle

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


class MarkPrimaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-primary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        iface = IPrimaryArticle
        
        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=iface.__module__+'.'+iface.__name__)

        if existing:
            elem = existing[0].getObject()
            context = aq_inner(elem)
            noLongerProvides(context, iface)
            context.reindexObject(idxs=['object_provides'])
            
        context = aq_inner(self.context)

        alsoProvides(context, iface)
        context.reindexObject(idxs=['object_provides'])

        IStatusMessage(self.request).addStatusMessage("Elemento marcado como principal para portada", type='info')
        view_url = context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "mark-primary-article"


class MarkSecondaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-secondary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        iface = ISecondaryArticle

        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=iface.__module__+'.'+iface.__name__)

        if len(existing) > 3:
            elem = existing[3].getObject()
            context = aq_inner(elem)
            noLongerProvides(context, iface)
            context.reindexObject(idxs=['object_provides'])

        context = aq_inner(self.context)

        alsoProvides(context, iface)
        context.reindexObject(idxs=['object_provides'])

        IStatusMessage(self.request).addStatusMessage("Elemento marcado como secundario para portada", type='info')
        view_url = context.absolute_url()
        self.request.response.redirect(view_url)
        
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
                   'primary' : IPrimaryArticle,
                   'secondary' : ISecondaryArticle
                  }

        return not ifaces[atype].providedBy(self.context)

    def render(self):
        return self

