# -*- coding: utf-8 -*-

from five import grok

from zope.interface import Interface
from zope.publisher.interfaces import NotFound

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName

from collective.nitf.browser import View
from collective.nitf.content import INITF
from collective.routes.interfaces import IFragmentContext
from collective.routes.interfaces import IWrappedBrainsContext
from collective.routes.interfaces import IWrappedObjectContext
from collective.routes import getObject

from telesur.theme.interfaces import ITelesurLayer

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


class Subscription(grok.View):
    """ Implemeta la subscripicion al newsletter de imoko mediante la carga
        en un iframe, para luego poder mostrar la página de resultado en el
        mismo iframe.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")

    def iframe_src(self):
        """ Retorna la url a ser incluida en el ifram.
        """
        portal_url = getToolByName(self.context, 'portal_url')
        return "%s/%s" % (portal_url(), 'subscriptionform')


class SubscriptionForm(grok.View):
    """ Implementa el formulario de subscription al newsletter de imoko.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")

    def processed_form(self):
        """ Si el formulario es procesado por el sistema de imoko correctamente,
            hace un redirect a una url indicada en el field 'pagOk' del form.
            Esta metodo indica si el procesamiento se dio correctamente.

            En caso de que el proceso de la subscripción falle imoko no hace el
            redirect sino que muestra el mensaje en una pagina de su servidor.

            La variable respuesta que es enviada via el redirect tiene un string
            con un mensaje que es preferible ignorar por cuestiones de
            seguridad.

            El formulario fue procesado por imoko.
            @return True

            Se carga el formulario para ser completado por el usuario.
            @return False

        """
        return self.request.get('respuesta', None) is not None
