# -*- coding: utf-8 -*-

from zope.interface import Interface

from plone.theme.interfaces import IDefaultPloneLayer


class ITelesurLayer(IDefaultPloneLayer):
    """ Default browser layer for telesur.policy """

class ITelesurViewlet(Interface):
    """ A marker interface for viewlets for queries with lists"""
