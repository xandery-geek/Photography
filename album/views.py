#!/usr/bin/env python
# -*- coding: utf-8 -*-

from django.shortcuts import render
from django.http import HttpRequest, FileResponse, JsonResponse
from django.views.generic import View, DetailView, ListView
from django.core.exceptions import MultipleObjectsReturned, ObjectDoesNotExist

from album.models import Album, AlbumImage


class RequestException(Exception):
    pass


class AlbumView(View):
    def get(self, request, *args, **kwargs):
        try:
            category = Album.CATE_MAP[kwargs['category']]
        except KeyError:
            category = Album.GALLERY

        album_list = Album.objects.filter(is_visible=True, category=category).order_by('-created')

        content = {'albums': album_list}
        return render(request, 'album.html', content)


class ImageList(ListView):
    album_model = Album
    model = AlbumImage
    paginate_by = 12
    template_name = 'image_list.html'

    def get_queryset(self):
        query_set = super(ImageList, self).get_queryset()
        try:
            album = self.album_model._default_manager.get(id=self.kwargs['album_id'], is_visible=True)
            query_set = query_set.filter(album=album)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            query_set = None

        return query_set

    def get_context_data(self, *, object_list=None, **kwargs):
        try:
            album = self.album_model._default_manager.get(id=self.kwargs['album_id'], is_visible=True)
            context = {"album": album}
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            context = {}

        return super().get_context_data(**context)


class ImageDetail(DetailView):
    model = AlbumImage
    pk_url_kwarg = 'image_id'
    template_name = 'image_detail.html'

    def get(self, request, *args, **kwargs):
        try:
            return super(ImageDetail, self).get(request, *args, **kwargs)
        except RequestException:
            return handler404(request, RequestException)

    def get_context_data(self, **kwargs):
        context = {}
        if self.object:
            context['image'] = self.object
            context_object_name = self.get_context_object_name(self.object)
            if context_object_name:
                context[context_object_name] = self.object
        else:
            raise RequestException()

        context.update(kwargs)
        return super().get_context_data(**context)


class OperationView(View):

    model = AlbumImage
    operation = ['like', 'download']

    def get(self, request, *args, **kwargs):
        pk = kwargs["image_id"]
        option = kwargs['option']
        try:
            image = self.model._default_manager.get(id=pk)
        except (ObjectDoesNotExist, MultipleObjectsReturned):
            return handler404(request, RequestException)

        if option in OperationView.operation:
            handle = getattr(self, 'on_' + option)
            return handle(image)
        else:
            return handler404(request, RequestException)

    @staticmethod
    def on_like(image):
        image.like_num += 1
        image.save()
        return JsonResponse({"Finished": True, "like_num": image.like_num})

    @staticmethod
    def on_download(image):
        file = open(image.image.path, 'rb')
        response = FileResponse(file)
        response['Content-Type'] = 'application/octet-stream'
        response['Content-Disposition'] = 'attachment;filename="{}"'.format(image.alt)
        return response


def handler404(request, exception):
    assert isinstance(request, HttpRequest)
    return render(request, 'handler404.html', None, None, 404)
