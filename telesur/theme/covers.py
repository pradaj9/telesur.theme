# -*- coding: utf-8 -*-
import uuid
import json
from urlparse import urlparse

from Acquisition import aq_base
from BTrees.OOBTree import OOBTree
from five import grok

from zope.annotation.interfaces import IAnnotations
from zope.component import getMultiAdapter
from zope.container.interfaces import INameChooser
from zope.interface import Interface
from zope.security import checkPermission

from plone.uuid.interfaces import IUUID
from plone.app.uuid.utils import uuidToObject
from Products.CMFCore.utils import getToolByName

from collective.nitf.content import INITF

from telesur.theme.interfaces import ITelesurLayer
from telesur.theme import config

grok.templatedir("covers")


class CoversView(grok.View):
    """ Manage covers selection in home page """
    grok.context(Interface)
    grok.name('covers-view')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoversView, self).__init__(context, request)

        layout_id = ''
        if 'layout_id' in self.request:
            layout_id = self.request['layout_id']

        remove = ''
        if 'remove' in self.request:
            remove = self.request['remove']

        make_default = ''
        if 'make_default' in self.request:
            make_default = self.request['make_default']

        if remove:
            self.remove_layout(layout_id)

        if not(remove) and make_default and layout_id:
            self.make_default(layout_id)

    def render(self):
        return ''

    def layout_conf(self):
        #we check if the annotation exist, if not, we should create an empty
        #one
        annotations = IAnnotations(aq_base(self.context), None)
        if not config.COVERS_KEYS in annotations:
            layout = OOBTree()
            layout['default_view'] = OOBTree()
            layout['views'] = OOBTree()
            annotations[config.COVERS_KEYS] = layout

        return annotations

    def add_layout(self, layout_id, layout_data):
        conf = self.layout_conf()[config.COVERS_KEYS]
        conf['views'][layout_id] = layout_data
        return conf

    def get_layout(self, layout_id=None):
        conf = self.layout_conf()[config.COVERS_KEYS]
        layout = {}
        if layout_id:
            layout = conf['views'][layout_id]
        else:
            layout = conf['default_view']
        return layout

    def views(self, view_id, draft_id):

        conf = self.layout_conf()
        view = {}
        if view_id in conf:
            if draft_id in conf['views'][view_id]:
                view = conf['views'][view_id][draft_id]

        return view

    def make_default(self, layout_id):
        conf = self.layout_conf()[config.COVERS_KEYS]
        uuid_layout_id = layout_id
        draft = conf['views'][uuid_layout_id]
        if draft:
            conf['default_view'] = draft
            del(conf['views'][uuid_layout_id])

        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)
        return

    def remove_layout(self, layout_id=None):
        conf = self.layout_conf()[config.COVERS_KEYS]
        if layout_id:
            del(conf['views'][layout_id])
        else:
            conf['default_view'] = OOBTree()
        view_url = self.context.absolute_url()
        self.request.response.redirect(view_url)
        return


class CoverControls(grok.View):
    grok.context(Interface)
    grok.name('cover-controls')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoverControls, self).__init__(context, request)
        covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
        self.covers_conf = covers_view.layout_conf()[config.COVERS_KEYS]
        self.conf = config.COVERS_VIEWS

    def default_view(self):
        self.default_view_title = 'por defecto'
        self.default_view_type = 'por defecto'

        df = self.covers_conf['default_view']
        if df:
            self.default_view_title = df['draft_title']
            self.default_view_type = self.conf[df['type']]['friendly-name']

    def get_edit_view(self, view_type=None, layout_id=None):
        if layout_id:
            view_type = self.covers_conf['views'][layout_id]['type']
        edit = self.conf[view_type]['edit']
        return edit

    def can_manage_covers(self):
        can_manage = checkPermission('telesur.theme.coverAddable', self.context)
        return can_manage

    def drafts(self):
        drafts = []
        views = self.covers_conf['views']
        for draft in views:
            drafts.append(draft)

        return views


class CoverElection(grok.View):
    grok.context(Interface)
    grok.name('cover-election')
    grok.template('cover_election')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoverElection, self).__init__(context, request)
        self.cover_id = ''
        if self.cover_id in self.request:
            self.cover_id = self.request['cover_id']

    def __call__(self):
        if self.request.method == 'POST':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = ''
            if 'layout_id' in self.request and self.request['layout_id']:
                layout_id = self.request['layout_id']
                data = covers_view.get_layout(layout_id)
            else:
                data = OOBTree({'type': 'election',
                        'draft_title': '',
                        'outstanding_new': '',
                        'image': '',
                        'image_link': '',
                        'twitter_hashtag': '',
                        'outstanding_new_uid': '',
                        'topic': '',
                        'topic_slug': ''})
                layout_id = str(uuid.uuid4())

            if 'draft-title' in self.request:
                data['draft_title'] = self.request['draft-title']

            if 'outstanding-new' in self.request:
                data['outstanding_new'] = self.request['outstanding-new']
                if 'outstanding-new-uid' in self.request:
                    uid = self.request['outstanding-new-uid']
                else:
                    path = urlparse(self.request['outstanding-new']).path
                    uid = ''
                    try:
                        path = self.context.restrictedTraverse(path)
                    except KeyError:
                        path = ''
                    if path:
                        uid = IUUID(path)
                data['outstanding_new_uid'] = uid

            namechooser = INameChooser(self.context)
            if 'uploadfile' in self.request and self.request['uploadfile']:
                uploadfile = self.request['uploadfile']
                id_name = namechooser.chooseName(uploadfile.filename, self.context)
                name_index = 0
                while name_index < 100:
                    try:
                        self.context.invokeFactory('Image', id=id_name, file=self.request['uploadfile'])
                        self.context[id_name].reindexObject()
                        data['image'] = self.context[id_name].UID()
                        name_index = 100
                    except:
                        pass
                    name_index = name_index + 1
                    id_name = id_name + '-' + str(name_index)

            if 'image-link' in self.request:
                data['image_link'] = self.request['image-link']

            if 'hashtag-twitter' in self.request:
                data['twitter_hashtag'] = self.request['hashtag-twitter']

            if 'topic' in self.request:
                data['topic'] = self.request['topic']

            if 'topic-slug' in self.request:
                data['topic_slug'] = self.request['topic-slug']
            #lets create the draft
            cover_data  = covers_view.add_layout(layout_id, data)

            #craft the redirect url
            view_url = self.context.absolute_url()
            draft_url = view_url + '?layout_id='+ str(layout_id)
            self.request.response.redirect(draft_url)

        elif 'layout_id' in self.request and self.request['formaction'] == 'edit':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = self.request['layout_id']
            data = covers_view.get_layout(layout_id)
            #lets craft the request with form variables
            self.request['draft-title'] = data['draft_title']
            self.request['outstanding-new'] = data['outstanding_new']
            self.request['outstanding-new-uid'] = data['outstanding_new_uid']
            self.request['hashtag-twitter'] = data['twitter_hashtag']
            self.request['image'] = data['image']
            self.request['image-link'] = data['image_link']
            self.request['topic'] = data['topic']
            self.request['topic-slug'] = data['topic_slug']

        return self.template.render(self)


class CoverSportingEvent(grok.View):
    grok.context(Interface)
    grok.name('cover-sporting-event')
    grok.template('cover_sporting_event')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoverSportingEvent, self).__init__(context, request)
        self.cover_id = ''
        if self.cover_id in self.request:
            self.cover_id = self.request['cover_id']

    def __call__(self):
        if self.request.method == 'POST':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = ''
            if 'layout_id' in self.request and self.request['layout_id']:
                layout_id = self.request['layout_id']
                data = covers_view.get_layout(layout_id)
            else:
                data = OOBTree({'type': 'sporting-event',
                        'draft_title': '',
                        'outstanding_new': '',
                        'image': '',
                        'image_link':'',
                        'outstanding_new_uid': '',
                        'topic': '',
                        'topic_slug': ''})
                layout_id = str(uuid.uuid4())

            if 'draft-title' in self.request:
                data['draft_title'] = self.request['draft-title']

            if 'outstanding-new' in self.request:
                data['outstanding_new'] = self.request['outstanding-new']
                if 'outstanding-new-uid' in self.request:
                    uid = self.request['outstanding-new-uid']
                else:
                    path = urlparse(self.request['outstanding-new']).path
                    uid = ''
                    try:
                        path = self.context.restrictedTraverse(path)
                    except KeyError:
                        path = ''
                    if path:
                        uid = IUUID(path)
                data['outstanding_new_uid'] = uid

            namechooser = INameChooser(self.context)
            if 'uploadfile' in self.request and self.request['uploadfile']:
                uploadfile = self.request['uploadfile']
                id_name = namechooser.chooseName(uploadfile.filename, self.context)
                name_index = 0
                while name_index < 100:
                    try:
                        self.context.invokeFactory('Image', id=id_name, file=self.request['uploadfile'])
                        self.context[id_name].reindexObject()
                        data['image'] = self.context[id_name].UID()
                        name_index = 100
                    except:
                        pass
                    name_index = name_index + 1
                    id_name = id_name + '-' + str(name_index)

            if 'image-link' in self.request:
                data['image_link'] = self.request['image-link']

            if 'topic' in self.request:
                data['topic'] = self.request['topic']

            if 'topic-slug' in self.request:
                data['topic_slug'] = self.request['topic-slug']

            #lets create the draft
            cover_data  = covers_view.add_layout(layout_id, data)

            #craft the redirect url
            view_url = self.context.absolute_url()
            draft_url = view_url + '?layout_id='+ str(layout_id)
            self.request.response.redirect(draft_url)

        elif 'layout_id' in self.request and self.request['formaction'] == 'edit':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = self.request['layout_id']
            data = covers_view.get_layout(layout_id)
            #lets craft the request with form variables
            self.request['draft-title'] = data['draft_title']
            self.request['outstanding-new'] = data['outstanding_new']
            self.request['outstanding-new-uid'] = data['outstanding_new_uid']            
            self.request['image'] = data['image']
            self.request['image-link'] = data['image_link']
            self.request['topic'] = data['topic']
            self.request['topic-slug'] = data['topic_slug']

        return self.template.render(self)


class CoverSpecial(grok.View):
    grok.context(Interface)
    grok.name('cover-special')
    grok.template('cover_special')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoverSpecial, self).__init__(context, request)
        self.cover_id = ''
        if self.cover_id in self.request:
            self.cover_id = self.request['cover_id']

    def __call__(self):
        if self.request.method == 'POST':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = ''
            if 'layout_id' in self.request and self.request['layout_id']:
                layout_id = self.request['layout_id']
                data = covers_view.get_layout(layout_id)
            else:
                data = OOBTree({'type': 'special',
                        'draft_title': '',
                        'outstanding_new': '',
                        'image': '',
                        'image_link':'',
                        'outstanding_new_uid': '',
                        'topic': '',
                        'topic_slug': ''})
                layout_id = str(uuid.uuid4())

            if 'draft-title' in self.request:
                data['draft_title'] = self.request['draft-title']

            if 'outstanding-new' in self.request:
                data['outstanding_new'] = self.request['outstanding-new']
                if 'outstanding-new-uid' in self.request:
                    uid = self.request['outstanding-new-uid']
                else:
                    path = urlparse(self.request['outstanding-new']).path
                    uid = ''
                    try:
                        path = self.context.restrictedTraverse(path)
                    except KeyError:
                        path = ''
                    if path:
                        uid = IUUID(path)
                data['outstanding_new_uid'] = uid

            namechooser = INameChooser(self.context)
            if 'uploadfile' in self.request and self.request['uploadfile']:
                uploadfile = self.request['uploadfile']
                id_name = namechooser.chooseName(uploadfile.filename, self.context)
                name_index = 0
                while name_index < 100:
                    try:
                        self.context.invokeFactory('Image', id=id_name, file=self.request['uploadfile'])
                        self.context[id_name].reindexObject()
                        data['image'] = self.context[id_name].UID()
                        name_index = 100
                    except:
                        pass
                    name_index = name_index + 1
                    id_name = id_name + '-' + str(name_index)

            if 'image-link' in self.request:
                data['image_link'] = self.request['image-link']

            if 'topic' in self.request:
                data['topic'] = self.request['topic']

            if 'topic-slug' in self.request:
                data['topic_slug'] = self.request['topic-slug']

            #lets create the draft
            cover_data  = covers_view.add_layout(layout_id, data)

            #craft the redirect url
            view_url = self.context.absolute_url()
            draft_url = view_url + '?layout_id='+ str(layout_id)
            self.request.response.redirect(draft_url)

        elif 'layout_id' in self.request and self.request['formaction'] == 'edit':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = self.request['layout_id']
            data = covers_view.get_layout(layout_id)
            #lets craft the request with form variables
            self.request['draft-title'] = data['draft_title']
            self.request['outstanding-new'] = data['outstanding_new']
            self.request['outstanding-new-uid'] = data['outstanding_new_uid']            
            self.request['image'] = data['image']
            self.request['image-link'] = data['image_link']
            self.request['topic'] = data['topic']
            self.request['topic-slug'] = data['topic_slug']

        return self.template.render(self)


class CoverGeneralEvent(grok.View):
    grok.context(Interface)
    grok.name('cover-general-event')
    grok.template('cover_general_event')
    grok.layer(ITelesurLayer)
    grok.require('cmf.ModifyPortalContent')

    def __init__(self, context, request):
        super(CoverGeneralEvent, self).__init__(context, request)
        self.cover_id = ''
        if self.cover_id in self.request:
            self.cover_id = self.request['cover_id']

    def __call__(self):
        if self.request.method == 'POST':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = ''
            if 'layout_id' in self.request and self.request['layout_id']:
                layout_id = self.request['layout_id']
                data = covers_view.get_layout(layout_id)
            else:
                data = OOBTree({'type': 'general-event',
                        'draft_title': '',
                        'outstanding_new': '',
                        'image': '',
                        'image_link':'',
                        'twitter_hashtag': '',
                        'outstanding_new_uid': '',
                        'topic': '',
                        'topic_slug': ''})
                layout_id = str(uuid.uuid4())

            if 'draft-title' in self.request:
                data['draft_title'] = self.request['draft-title']

            if 'outstanding-new' in self.request:
                data['outstanding_new'] = self.request['outstanding-new']
                if 'outstanding-new-uid' in self.request:
                    uid = self.request['outstanding-new-uid']
                else:
                    path = urlparse(self.request['outstanding-new']).path
                    uid = ''
                    try:
                        path = self.context.restrictedTraverse(path)
                    except KeyError:
                        path = ''
                    if path:
                        uid = IUUID(path)
                data['outstanding_new_uid'] = uid

            namechooser = INameChooser(self.context)
            if 'uploadfile' in self.request and self.request['uploadfile']:
                uploadfile = self.request['uploadfile']
                id_name = namechooser.chooseName(uploadfile.filename, self.context)
                name_index = 0
                while name_index < 100:
                    try:
                        self.context.invokeFactory('Image', id=id_name, file=self.request['uploadfile'])
                        self.context[id_name].reindexObject()
                        data['image'] = self.context[id_name].UID()
                        name_index = 100
                    except:
                        pass
                    name_index = name_index + 1
                    id_name = id_name + '-' + str(name_index)

            if 'image-link' in self.request:
                data['image_link'] = self.request['image-link']

            if 'topic' in self.request:
                data['topic'] = self.request['topic']

            if 'topic-slug' in self.request:
                data['topic_slug'] = self.request['topic-slug']

            if 'hashtag-twitter' in self.request:
                data['twitter_hashtag'] = self.request['hashtag-twitter']

            #lets create the draft
            cover_data  = covers_view.add_layout(layout_id, data)

            #craft the redirect url
            view_url = self.context.absolute_url()
            draft_url = view_url + '?layout_id='+ str(layout_id)
            self.request.response.redirect(draft_url)

        elif 'layout_id' in self.request and self.request['formaction'] == 'edit':
            covers_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
            layout_id = self.request['layout_id']
            data = covers_view.get_layout(layout_id)
            #lets craft the request with form variables
            self.request['draft-title'] = data['draft_title']
            self.request['outstanding-new'] = data['outstanding_new']
            self.request['outstanding-new-uid'] = data['outstanding_new_uid']            
            self.request['hashtag-twitter'] = data['twitter_hashtag']
            self.request['image'] = data['image']
            self.request['image-link'] = data['image_link']
            self.request['topic'] = data['topic']
            self.request['topic-slug'] = data['topic_slug']

        return self.template.render(self)


class BaseLayout(grok.View):
    grok.context(Interface)
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(BaseLayout, self).__init__(context, request)
        self.layout_helper = getMultiAdapter((self.context, self.request),
                                            name='layout-helper')

        layout_id = self.request['layout_id'] if 'layout_id' in self.request else None

        cover_view = getMultiAdapter((self.context, self.request),
                                            name='covers-view')
        self.cover = cover_view.get_layout(layout_id)

        self.outstanding = uuidToObject(self.cover['outstanding_new_uid'])

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

    def get_multimedia(self, obj, thumb=False):
        multimedia = self.layout_helper.get_multimedia(obj, thumb)
        return multimedia

    def get_cover_image(self):
        img = ''
        if 'image' in self.cover:
            img = uuidToObject(self.cover['image'])
        return img

    def get_cover_twitter(self):
        hashtag = ''
        if 'twitter_hashtag' in self.cover:
            hashtag = self.cover['twitter_hashtag']
        return hashtag


class CoverElectionLayout(BaseLayout):
    grok.context(Interface)
    grok.name('cover-election-layout')
    grok.template('cover_election_layout')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(CoverElectionLayout, self).__init__(context, request)


class CoverSportingEventLayout(BaseLayout):
    grok.context(Interface)
    grok.name('cover-sporting-event-layout')
    grok.template('cover_sporting_event_layout')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(CoverSportingEventLayout, self).__init__(context, request)


class CoverSpecialLayout(BaseLayout):
    grok.context(Interface)
    grok.name('cover-special-layout')
    grok.template('cover_special_layout')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(CoverSpecialLayout, self).__init__(context, request)


class CoverGeneralEventLayout(BaseLayout):
    grok.context(Interface)
    grok.name('cover-general-event-layout')
    grok.template('cover_general_event_layout')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def __init__(self, context, request):
        super(CoverGeneralEventLayout, self).__init__(context, request)


class NewsListSearch(grok.View):
    grok.context(Interface)
    grok.name('news-list-search')
    grok.layer(ITelesurLayer)
    grok.require('zope2.View')

    def update(self):

        if 'text' in self.request:
            catalog = getToolByName(self.context, 'portal_catalog')            
            #query build getting all the section news
            limit = 10;
            query = {}
            query['object_provides'] = {'query': [INITF.__identifier__]}
            query['sort_on'] = 'effective'
            query['sort_order'] = 'reverse'
            query['sort_limit'] = limit

            self.existing = catalog.searchResults(query)

    def process_query(self, query):
        
        q = {}
        for brain in query:
            obj = brain.getObject()
            uuid = IUUID(obj, None)
            q[str(uuid)] = {
                'title': obj.title, 
                'url':obj.absolute_url(),
                'uuid':str(uuid)
            }
        return q

    def render(self):
        result = self.process_query(self.existing)
        if result:
            result = json.dumps(result)

        return result
