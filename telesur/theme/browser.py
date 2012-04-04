# -*- coding: utf-8 -*-
from AccessControl import ClassSecurityInfo
from five import grok

from zope.component import getMultiAdapter

from zope.interface import Interface
from zope.annotation.interfaces import IAnnotations

from Products.CMFCore.interfaces import IFolderish
from Products.CMFCore.utils import getToolByName

from Products.CMFPlone.PloneBatch import Batch

from collective.nitf.browser import View
from collective.nitf.content import INITF

from telesur.theme.interfaces import ITelesurLayer
from telesur.theme.interfaces import IOutstandingArticle
from telesur.theme.interfaces import IPrimaryArticle
from telesur.theme.interfaces import ISecondaryArticle
from telesur.theme.interfaces import ISectionArticle

from Acquisition import aq_inner
from zope.interface import alsoProvides, noLongerProvides

from Products.statusmessages.interfaces import IStatusMessage

from plone.directives import dexterity

import DateTime

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

    def pub_date(self):
        weekdays = ['Domingo', 'Lunes', 'Martes', 'Miércoles', 'Jueves',
                    'Viernes', 'Sábado']
        months = ['Enero', 'Febrero', 'Marzo', 'Abril',
                  'Mayo', 'Junio', 'Julio', 'Agosto',
                  'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']

        self.date = ''
        effective = self.context.effective_date
        if effective:
            weekday = effective.strftime('%w')
            day = int(effective.strftime('%d'))
            month = effective.strftime('%m')
            year = effective.strftime('%Y')
            w = int(weekday)
            m = int(month) - 1
            hour = effective.strftime('%I')
            minute = effective.strftime('%M')
            timeofday = effective.strftime('%P')
            self.date = '%s %s de %s de %s, %s:%s %s' % (weekdays[w],
                                                         day,
                                                         months[m],
                                                         year,
                                                         hour,
                                                         minute,
                                                         timeofday)

        return self.date


class Media(dexterity.DisplayForm):
    grok.context(INITF)
    grok.require('cmf.ModifyPortalContent')
    grok.layer(ITelesurLayer)

    def has_videos(self):
        view = getMultiAdapter((self.context, self.request), name='nota')
        videos = []
        if view:
            context_path = '/'.join(self.context.getPhysicalPath())
            query = {'Type': ('Link',)}
            query['path'] = {'query': context_path,
                             'depth': 1, }
            query['sort_on'] = 'getObjPositionInParent'
            query['limit'] = None

            results = self.context.getFolderContents(contentFilter=query,
                                                     batch=False,
                                                     b_size=10,
                                                     full_objects=False)

            for link in results:
                link_obj = link.getObject()
                annotations = IAnnotations(link_obj)
                is_video = annotations.get('thumbnail_pequeno', None)
                if is_video:
                    videos.append({'obj': link,
                                   'url': link_obj.absolute_url() + '/@@thumbnail_mediano'})

        return videos


class Folder_Summary_View(grok.View):
    grok.context(IFolderish)
    grok.name("folder_summary_view")
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")


class GoogleMapView(grok.View):
    grok.context(Interface)
    grok.name("mapa")
    grok.layer(ITelesurLayer)
    grok.require("zope2.View")


class Opinion(grok.View):
    """Vista para artículo de opinión.
    """
    grok.context(INITF)
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')


class Special_Report(grok.View):
    """Vista para reportaje especial.

    Prueba de concepto; el archivo flash principal se debe llamar main.swf
    """
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
        """ Si el formulario es procesado por el sistema de imoko
            correctamente, hace un redirect a una url indicada en el field
            'pagOk' del form. Esta metodo indica si el procesamiento se dio
            correctamente.

            En caso de que el proceso de la subscripción falle imoko no hace
            el redirect sino que muestra el mensaje en una pagina de su
            servidor.

            La variable respuesta que es enviada via el redirect tiene un
            string con un mensaje que es preferible ignorar por cuestiones de
            seguridad.

            El formulario fue procesado por imoko.
            @return True

            Se carga el formulario para ser completado por el usuario.
            @return False

        """
        return self.request.get('respuesta', None) is not None


class MarkOutstandingArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-outstanding-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        ac = getMultiAdapter((self.context, self.request),
                             name="article-control")
        ac.mark_outstanding(self.context)
        IStatusMessage(self.request).addStatusMessage(u"Elemento marcado como destacado para portada.", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "mark-outstanding-article"


class MarkPrimaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-primary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        ac = getMultiAdapter((self.context, self.request),
                             name="article-control")
        ac.mark_primary(self.context)
        IStatusMessage(self.request).addStatusMessage(u"Elemento marcado como principal para portada", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "mark-primary-article"


class MarkSecondaryArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-secondary-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        ac = getMultiAdapter((self.context, self.request),
                             name="article-control")
        ac.mark_secondary(self.context)
        IStatusMessage(self.request).addStatusMessage(u"Elemento marcado como secundario para portada", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "mark-secondary-article"


class MarkSectionArticle(grok.View):
    grok.context(INITF)
    grok.name("mark-section-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        ac = getMultiAdapter((self.context, self.request),
                             name="article-control")
        ac.mark_section(self.context)
        IStatusMessage(self.request).addStatusMessage(u"Elemento marcado como destacado de sección", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "mark-section-article"


class UnmarkArticle(grok.View):
    grok.context(INITF)
    grok.name("unmark-article")
    grok.require("cmf.ModifyPortalContent")

    def __call__(self):
        ac = getMultiAdapter((self.context, self.request),
                             name="article-control")
        ac.unmark(self.context)
        IStatusMessage(self.request).addStatusMessage(u"El elemento fue desmarcado", type='info')
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)

    def render(self):
        return "unmark-article"


class ArticleControl(grok.View):
    grok.context(INITF)
    grok.name("article-control")
    grok.require("cmf.ModifyPortalContent")

    security = ClassSecurityInfo()

    security.declarePublic('can_be_promoted')
    security.declarePublic('is_published')

    def is_published(self):
        workflowTool = getToolByName(self.context, 'portal_workflow')
        workFlow = workflowTool.getWorkflowsFor(self.context)
        state = None
        if workFlow:
            wf_def = workFlow[0]
            status = self.context.portal_workflow.getStatusOf(wf_def.getId(),
                self.context)
            if status:
                state = status["review_state"]
        return state == "published"

    def can_be_promoted(self, atype):
        return not self.already_marked(self.context, atype)

    def already_marked(self, element, atype):
        ifaces = {
                   'outstanding': IOutstandingArticle,
                   'primary': IPrimaryArticle,
                   'secondary': ISecondaryArticle,
                   'section': ISectionArticle,
                  }

        return ifaces[atype].providedBy(element)

    def unmark(self, element):

        catalog = getToolByName(self.context, 'portal_catalog')

        if element:
            has_outstanding = False
            has_primary = False
            if self.already_marked(element, 'outstanding'):
                noLongerProvides(element, IOutstandingArticle)

                element.reindexObject(idxs=['object_provides'])
                primary_list = catalog(object_provides=IPrimaryArticle.__identifier__,
                                    sort_on='effective', sort_order='reverse')
                if primary_list:
                    self.mark_outstanding(primary_list[0].getObject())
                has_outstanding = True

            if self.already_marked(element, 'primary') or has_outstanding:
                noLongerProvides(element, IPrimaryArticle)

                element.reindexObject(idxs=['object_provides'])
                secondary_list = catalog(object_provides=ISecondaryArticle.__identifier__,
                                    sort_on='effective', sort_order='reverse')

                if secondary_list:
                    self.mark_primary(secondary_list[0].getObject())
                has_primary = True

            if self.already_marked(element, 'secondary') or has_primary:
                noLongerProvides(element, ISecondaryArticle)
                element.reindexObject(idxs=['object_provides'])

            element.reindexObject(idxs=['object_provides'])

    def mark_outstanding(self, element):

        if self.already_marked(element, 'outstanding'):
            return

        iface_to_remove = [IPrimaryArticle, ISecondaryArticle]

        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=IOutstandingArticle.__identifier__)

        if existing:
            elem = existing[0].getObject()
            self.mark_primary(elem)

        context = aq_inner(element)
        alsoProvides(context, IOutstandingArticle)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)

        context.reindexObject(idxs=['object_provides'])

    def mark_primary(self, element):

        if self.already_marked(element, 'primary'):
            return

        iface_to_remove = [IOutstandingArticle, ISecondaryArticle]

        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=IPrimaryArticle.__identifier__,
                           sort_on='effective')

        if len(existing) > 3:
            elem = existing[0].getObject()
            self.mark_secondary(elem)

        context = aq_inner(element)
        alsoProvides(context, IPrimaryArticle)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)

        context.reindexObject(idxs=['object_provides'])

    def mark_secondary(self, element):

        if self.already_marked(element, 'secondary'):
            return

        iface_to_remove = [IOutstandingArticle, IPrimaryArticle]

        context = aq_inner(element)
        alsoProvides(context, ISecondaryArticle)
        for iface in iface_to_remove:
            noLongerProvides(context, iface)

        context.reindexObject(idxs=['object_provides'])

    def mark_section(self, element):

        if self.already_marked(element, 'section'):
            return

        catalog = getToolByName(self.context, 'portal_catalog')
        # search *only* in this section
        existing = catalog(object_provides=ISectionArticle.__identifier__,
                           section=element.section)

        # existe el caso donde se puede marcar una nota para una seccion,
        # luego cambiarle manualmente la misma, lo que nos dejaria con mas de
        # una *nota de seccion* por seccion
        for article in existing:
            elem = article.getObject()
            context = aq_inner(elem)
            noLongerProvides(context, ISectionArticle)
            context.reindexObject(idxs=['object_provides'])

        context = aq_inner(element)

        alsoProvides(context, ISectionArticle)
        context.reindexObject(idxs=['object_provides'])

    def render(self):
        return self


class HomeView(grok.View):
    """Vista para la home.
    """
    grok.context(Interface)
    grok.name('home-view')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(HomeView, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                            name='layout-helper')

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)
        return multimedia

    def outstanding(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        existing = catalog(object_provides=IOutstandingArticle.__identifier__)

        elem = ''
        if existing:
            elem = existing[0].getObject()

        return elem

    def primary(self):
        catalog = getToolByName(self.context, 'portal_catalog')
        elements = catalog(object_provides=IPrimaryArticle.__identifier__,
                           sort_on='effective', sort_order='reverse')

        return elements

    def secondary(self, limit=6):
        catalog = getToolByName(self.context, 'portal_catalog')
        elements = catalog(object_provides=ISecondaryArticle.__identifier__,
                           sort_on='effective', sort_order='reverse')

        return elements[:limit]

    def has_videos(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un vínculo a un
        video en el sistema multimedia.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            # FIXME: debemos comprobar que los links son vínculos al sistema
            # multimedia
            return view.has_links() > 0
        return False

    def has_gallery(self, obj):
        """ Retorna verdadero si el objeto contiene más de una imagen, o sea,
        una galería.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_images() > 1
        return False

    def has_atachments(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un archivo.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_files() > 0
        return False


class LayoutHelper(grok.View):
    """ Vista base para secciones
    """
    grok.context(Interface)
    grok.name('layout-helper')
    grok.require('zope2.View')

    def render(self):
        return self

    def get_multimedia(self, obj, thumb=False):
        obj = obj.getObject() if hasattr(obj, 'getObject') else obj
        multimedia = {'type': None, 'url': None, 'obj': None, 'description': None}
        if obj:
            context_path = '/'.join(obj.getPhysicalPath())
            query = {'Type': ('Link',)}
            query['path'] = {'query': context_path,
                             'depth': 1, }
            query['sort_on'] = 'getObjPositionInParent'
            query['limit'] = None

            results = obj.getFolderContents(contentFilter=query, batch=False,
                                            b_size=10, full_objects=False)

            if results:
                for link in results:
                    link_obj = link.getObject()
                    multimedia['obj'] = link_obj
                    multimedia['description'] = link_obj.Description()
                    annotations = IAnnotations(link_obj)
                    if thumb:
                        is_video = annotations.get('archivo_url', None)
                        multimedia['url'] = link_obj.absolute_url() + \
                            '/@@thumbnail_pequeno' if is_video else None
                        multimedia['type'] = 'thumb' if multimedia['url'] else None
                    else:
                        multimedia['url'] = annotations.get('archivo_url', None)
                        multimedia['type'] = 'video' if multimedia['url'] else None
                    break

            if not multimedia['url']:
                #we need to search for images because doesn't have videos
                query['Type'] = ('Image', )
                results = obj.getFolderContents(contentFilter=query,
                                                batch=False,
                                                b_size=10,
                                                full_objects=False)
                if results:
                    multimedia['url'] = results[0].getObject()
                    multimedia['type'] = 'image'
                    multimedia['obj'] = results[0].getObject()
                    multimedia['description'] = results[0].Description

        return multimedia

    def section(self, section=''):
        criterion = getattr(self.context,
                            'crit__section_ATSimpleStringCriterion', None)

        section_index = ''
        if not section:
            if criterion:
                section_index = criterion.value
            else:
                # XXX: deberiamos tener esto generalizado en una annotation en
                # el objeto bajo la variable "section"

                # por ahora vamos a buscar las colecciones hijas, el primer
                # elemento y usar el criterio de ahi
                catalog = getToolByName(self.context, 'portal_catalog')
                folder_path = '/'.join(self.context.getPhysicalPath())
                results = catalog(path={'query': folder_path, 'depth': 1},
                                  portal_type="Topic",
                                  sort_on='getObjPositionInParent',
                                  review_state='published')
                if results:
                    criterion = getattr(results[0].getObject(),
                                'crit__section_ATSimpleStringCriterion', None)

                section_index = criterion.value if criterion else ''
        else:
            section_index = section
        return section_index

    def articles(self, limit, genre='Current', all_articles=False,
                       outstanding_optional=False, section='', batched=False, b_start=0):

        elements = {'outstanding': [], 'secondary': [], 'articles': []}
        catalog = getToolByName(self.context, 'portal_catalog')

        section = self.section(section)

        #query build getting all the section news
        query = {}
        query['object_provides'] = {'query': [INITF.__identifier__]}
        query['sort_on'] = 'effective'
        query['sort_order'] = 'reverse'
        if not batched:
            query['sort_limit'] = limit + 1
        query['genre'] = genre
        query['review_state'] = 'published'

        #query build for outstanding news
        outstanding = {}
        outstanding['object_provides'] = {
        'query': [ISectionArticle.__identifier__]}
        outstanding['genre'] = genre
        outstanding['sort_on'] = 'effective'
        outstanding['sort_order'] = 'reverse'
        outstanding['sort_limit'] = 1
        outstanding['review_state'] = 'published'

        if section:
            query['section'] = section
            outstanding['section'] = section

        existing = catalog.searchResults(query)

        if all_articles:
            if batched:
                if(len(existing) > b_start):
                    elements['articles'] = Batch(existing, limit, b_start)
                else:
                    elements['articles'] = []
            else:
                elements['articles'] = existing[:limit]
        else:
            #queremos dividir los objetos en outstanding y otros
            if (existing and section) or (existing and outstanding_optional):
                outstanding_UID = 0
                outstanding_results = catalog.searchResults(outstanding)

                move = 0
                if outstanding_results:
                    elements['outstanding'].append(
                        outstanding_results[0].getObject())
                    outstanding_UID = outstanding_results[0].UID
                else:
                    elements['outstanding'].append(existing[0].getObject())
                    move = 1
                #batcheamos los objetos para paginacion
                if batched:
                    if b_start > limit:
                        move = 0
                    tmp_elements = filter(lambda nota: nota.UID != outstanding_UID,
                        existing)[move:]
                    if(len(existing) > b_start):
                        elements['secondary'] = Batch(tmp_elements, limit, b_start)
                    else:
                        elements['secondary'] = []
                else:
                    elements['secondary'] = \
                        filter(lambda nota: nota.UID != outstanding_UID,
                        existing)[move: limit + move]

            elif existing:
                #no es una seccion, sino una vista global
                elements['outstanding'] = [existing[0].getObject()]
                elements['secondary'] = existing[1: limit + 1]

        return elements


class SectionView(grok.View):
    """Vista para secciones.
    """
    # XXX: Esta vista utiliza el criterio de una coleccion para buscar
    # elementos de sección, se deberia reemplazar por una marker interface que
    # identifique la sección (o en su defecto que permita guardar en una
    # annotation en el objeto una categoría)
    grok.context(Interface)
    grok.name('section-view')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(SectionView, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                             name='layout-helper')

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)

        return multimedia

    def section(self):
        section_index = self.layout_helper.section()

        return section_index

    def articles(self, limit=8, section='', batched=False):
        elements = self.layout_helper.articles(limit, genre='Current',
                                               section=section)
        return elements

    def has_videos(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un vínculo a un
        video en el sistema multimedia.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            # FIXME: debemos comprobar que los links son vínculos al sistema
            # multimedia
            return view.has_links() > 0
        return False

    def has_gallery(self, obj):
        """ Retorna verdadero si el objeto contiene más de una imagen, o sea,
        una galería.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_images() > 1
        return False

    def has_atachments(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un archivo.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_files() > 0
        return False


class MoreArticles(grok.View):
    """Vista para traer mas articulos usando ajax.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('more-articles-view')
    grok.template('more_articles')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(MoreArticles, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                             name='layout-helper')

    def update(self):
        b_start = 8
        limit = 8
        kind = "Current"

        if 'kind' in self.request.keys():
            kind = self.request['kind']

        if 'b_start' in self.request.keys():
            b_start = int(self.request['b_start'])

        if kind == "Opinion":
            articles = self.layout_helper.articles(limit, genre='Opinion',
                    all_articles=True, batched=True,
                    b_start=b_start)
            self.articles = articles['articles']
        elif kind == "Current":
            articles = self.layout_helper.articles(limit, genre=kind,
                            batched=True, b_start=b_start)
            self.articles = articles['secondary']

        elif kind == "Interview":
            articles = self.layout_helper.articles(limit, genre='Interview',
                                        outstanding_optional=True, batched=True,
                                        b_start=b_start)
            self.articles = articles['secondary']

        elif kind == "Background":
            articles = self.layout_helper.articles(limit, genre='Background',
                                        outstanding_optional=True, batched=True,
                                        b_start=b_start)
            self.articles = articles['secondary']

        self.kind = kind

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)

        return multimedia

    def has_videos(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un vínculo a un
        video en el sistema multimedia.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            # FIXME: debemos comprobar que los links son vínculos al sistema
            # multimedia
            return view.has_links() > 0
        return False

    def has_gallery(self, obj):
        """ Retorna verdadero si el objeto contiene más de una imagen, o sea,
        una galería.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_images() > 1
        return False

    def has_atachments(self, obj):
        """ Retorna verdadero si el objeto contiene al menos un archivo.
        """
        view = getMultiAdapter((obj, self.request), name='nota')
        if view:
            return view.has_files() > 0
        return False


class OpinionView(grok.View):
    """Vista para seccion opinion.
    """
    # XXX: Esta vista utiliza el criterio de una coleccion para buscar
    # elementos de seccion, se deberia reemplazar por una marker interface que
    # identifique la seccion (o en su defecto que permita guardar en una
    # annotation en el objeto una categoria)
    grok.context(Interface)
    grok.name('opinion-view')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(OpinionView, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                             name='layout-helper')

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)

        return multimedia

    def section(self):
        section_index = self.layout_helper.section()

        return section_index

    def articles(self, limit=8, section=''):
        elements = self.layout_helper.articles(limit, genre='Opinion',
                    all_articles=True, section=section)

        return elements


class Opinion_InterviewView(grok.View):
    """Vista para seccion opinion.
    """
    # XXX: Esta vista utiliza el criterio de una coleccion para buscar
    # elementos de seccion, se deberia reemplazar por una marker interface que
    # identifique la seccion (o en su defecto que permita guardar en una
    # annotation en el objeto una categoria)
    grok.context(Interface)
    grok.name('opinion-interview-view')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(Opinion_InterviewView, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                             name='layout-helper')

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)
        return multimedia

    def section(self):
        section_index = self.layout_helper.section()

        return section_index

    def articles(self, limit=8):
        elements = self.layout_helper.articles(limit, genre='Interview',
                                               outstanding_optional=True)
        return elements


class Opinion_ContextView(grok.View):
    """Vista para seccion opinion.
    """
    # XXX: Esta vista utiliza el criterio de una coleccion para buscar
    # elementos de seccion, se deberia reemplazar por una marker interface que
    # identifique la seccion (o en su defecto que permita guardar en una
    # annotation en el objeto una categoria)
    grok.context(Interface)
    grok.name('opinion-context-view')
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(Opinion_ContextView, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                             name='layout-helper')

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)
        return multimedia

    def section(self):
        section_index = self.layout_helper.section()

        return section_index

    def articles(self, limit=8):
        elements = self.layout_helper.articles(limit, genre='Background',
                                               outstanding_optional=True)
        return elements


class Schedule(grok.View):
    """ Programación del canal.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')


class LiveSignal(grok.View):
    """ Señal en vivo del canal.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('live-signal')
    grok.template('live_signal')
    grok.require('zope2.View')


class LiveSignalBackup(grok.View):
    """ Señal en vivo del canal ULTRABASE.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('live-signal-backup')
    grok.template('live_signal_backup')
    grok.require('zope2.View')


class LiveAudio(grok.View):
    """ Audio en vivo del canal.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('live-audio')
    grok.template('live_audio')
    grok.require('zope2.View')


class BatchListUtils(grok.View):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('batch_list_utils')
    grok.require('zope2.View')

    def render(self):
        return self

    def two_per_iter_list(self, data):
        division = [x for x in range(len(data)) if x % 2 == 0]
        obj_list = [(data[x], len(data) - 1 > x and data[x + 1]) for x in division]
        return obj_list


class DondeDistribucion(grok.View):
    """ Distribucion del canal.
    """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('donde-distribucion')
    grok.template('donde_distribucion')
    grok.require('zope2.View')


class Rss2(grok.View):
    """ template rss2 """
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.name('rss2')
    grok.template('rss2')
    grok.require('zope2.View')

    def get_channel_pubdate(self):
        today = DateTime.DateTime().strftime('%m/%d/%Y')
        pubdate = DateTime.DateTime(today)

        return pubdate.rfc822()

    def get_item_pubdate(self, obj):
        effective = obj.effective_date and obj.effective()
        modified = obj.modified()
        date = effective or modified

        return date

    def get_objects_list(self):
        syn = self.context.portal_syndication
        obj_list = list(syn.getSyndicatableContent(self.context))

        return obj_list
