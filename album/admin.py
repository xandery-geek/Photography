#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import zipfile
import imghdr
from datetime import datetime
from io import BytesIO

from PIL import Image
from django.contrib import admin
from django.core.files.base import ContentFile

from Photograph import settings
from album.forms import AlbumForm, AlbumImageForm
from album.models import Album, AlbumImage

HORIZON_WIDTH = 480
HORIZON_HEIGHT = 360

VERTICAL_WIDTH = 360
VERTICAL_HEIGHT = 480


def convert_to_jpeg(img):
    if imghdr.what(img.path) == 'jpeg':
        return
    with Image.open(img.path) as i:
        i = i.convert('RGB')
        i.save(img.path, 'JPEG')


def rename_image_file(image, slug):
    initial_path = image.path
    base_path = os.path.dirname(initial_path)
    new_name = '{0}{1}.jpg'.format(slug, str(uuid.uuid4())[-13:])
    new_path = os.path.join(base_path, new_name)
    os.rename(initial_path, new_path)

    upload_to = os.path.dirname(image.name)
    image.name = os.path.join(upload_to, new_name)


def get_thumb_size(size):
    width, height = size
    if width > height:  # 横屏
        width, height = HORIZON_WIDTH, HORIZON_HEIGHT
    else:  # 竖屏
        width, height = VERTICAL_WIDTH, VERTICAL_HEIGHT

    return width, height


@admin.register(Album)
class AlbumModelAdmin(admin.ModelAdmin):
    form = AlbumForm
    prepopulated_fields = {'slug': ('title',)}
    list_display = ('title', 'thumb')
    list_filter = ('created',)

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            album = form.save(commit=False)
            album.modified = datetime.now()
            album.save()

            post_thumb = request.FILES.get("thumb", False)
            if post_thumb and post_thumb != "":
                rename_image_file(album.thumb, album.slug)
                convert_to_jpeg(album.thumb)
                with Image.open(album.thumb.path) as i:
                    width, height = get_thumb_size(i.size)
                    i.thumbnail((width, height), Image.ANTIALIAS)
                    i.save(album.thumb.path, 'JPEG')
                album.save()

            if form.cleaned_data['zip'] is not None:
                zip_images = zipfile.ZipFile(form.cleaned_data['zip'])
                for filename in sorted(zip_images.namelist()):
                    file_name = os.path.basename(filename)
                    if not file_name:
                        continue

                    data = zip_images.read(filename)
                    content_file = ContentFile(data)

                    # save image
                    img = AlbumImage()
                    img.album = album
                    filename = '{0}{1}.jpg'.format(album.slug, str(uuid.uuid4())[-13:])
                    img.alt = filename
                    img.image.save(filename, content_file)

                    # save thumb image
                    thumb_filename = 'thumb-{0}'.format(filename)
                    img.thumb.save(thumb_filename, content_file)

                    convert_to_jpeg(img.image)
                    convert_to_jpeg(img.thumb)

                    # get image size and resize thumb image
                    thumb_filepath = '{0}/albums/{1}'.format(settings.MEDIA_ROOT, thumb_filename)
                    with Image.open(thumb_filepath) as i:
                        img.width, img.height = i.size
                        i.thumbnail(get_thumb_size(i.size), Image.ANTIALIAS)
                        i.save(thumb_filepath, 'JPEG')

                    img.save()
                zip_images.close()
            super(AlbumModelAdmin, self).save_model(request, obj, form, change)


# In case image should be removed from album.
@admin.register(AlbumImage)
class AlbumImageModelAdmin(admin.ModelAdmin):
    form = AlbumImageForm
    list_display = ('alt', 'album')
    list_filter = ('album', 'created')

    def save_model(self, request, obj, form, change):
        if form.is_valid():
            img = form.save(commit=False)

            img.created = datetime.now()
            img.slug = img.album.slug
            img.album.modified = datetime.now()
            img.save()

            post_image = request.FILES.get("image", False)
            if not post_image or post_image == "":
                return

            # save the new image
            rename_image_file(img.image, img.slug)
            convert_to_jpeg(img.image)
            img.width, img.height = img.image.width, img.image.height

            filename = img.image.name
            img.alt = os.path.basename(filename)

            img_file = Image.open(img.image.path)

            # save image to tmp direction
            thumb_filename = 'thumb-{0}'.format(img.alt)
            thumb_img = img_file.copy()
            thumb_img.thumbnail(get_thumb_size((img.width, img.height)), Image.ANTIALIAS)

            # save image to django file
            thumb_io = BytesIO()
            thumb_img.save(fp=thumb_io, format='JPEG')
            img.thumb.save(thumb_filename, ContentFile(thumb_io.getvalue()))

            img.save()

        super(AlbumImageModelAdmin, self).save_model(request, obj, form, change)
