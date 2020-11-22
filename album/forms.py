#!/usr/bin/env python
# -*- coding: utf-8 -*-
from django import forms
from album.models import Album, AlbumImage


class AlbumForm(forms.ModelForm):
    class Meta:
        model = Album
        exclude = []

    zip = forms.FileField(required=False)


class AlbumImageForm(forms.ModelForm):

    class Meta:
        model = AlbumImage
        exclude = []
