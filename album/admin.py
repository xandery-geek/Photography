#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
import zipfile
from datetime import datetime
from io import BytesIO

from PIL import Image
from django.contrib import admin
from django.core.files.base import ContentFile

from Photograph import settings
from album.forms import AlbumForm, AlbumImageForm
from album.models import Album, AlbumImage

HORIZON_WIDTH = 320
HORIZON_HEIGHT = 240

VERTICAL_WIDTH = 240
VERTICAL_HEIGHT = 320


def convert_to_jpeg(img):
    img = img.convert('JPEG')
    return img


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
                    img.alt = filename
                    filename = '{0}{1}.jpg'.format(album.slug, str(uuid.uuid4())[-13:])
                    img.image.save(filename, content_file)

                    # save thumb image
                    thumb_filename = 'thumb-{0}'.format(filename)
                    img.thumb.save(thumb_filename, content_file)

                    # get image size and set thumb size
                    filepath = '{0}/albums/{1}'.format(settings.MEDIA_ROOT, filename)
                    with Image.open(filepath) as i:
                        img.width, img.height = i.size
                        if img.width > img.height:  # 横屏
                            thumb_width, thumb_height = HORIZON_WIDTH, HORIZON_HEIGHT
                        else:  # 竖屏
                            thumb_width, thumb_height = VERTICAL_WIDTH, VERTICAL_HEIGHT

                    # resize thumb image
                    thumb_filepath = '{0}/albums/{1}'.format(settings.MEDIA_ROOT, thumb_filename)
                    with Image.open(thumb_filepath) as i:
                        i.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)
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

            post_image = request.POST.get("image", False)
            if post_image or post_image == "":
                img.save()
                return

            # save the new image
            img.width = img.image.width
            img.height = img.image.height

            filename = str(img.image)
            img.alt = filename

            if img.width > img.height:  # 横屏
                thumb_width, thumb_height = HORIZON_WIDTH, HORIZON_HEIGHT
            else:  # 竖屏
                thumb_width, thumb_height = VERTICAL_WIDTH, VERTICAL_HEIGHT

            img_file = Image.open(img.image)

            # save image to tmp direction
            thumb_filename = 'thumb-{0}'.format(filename)
            thumb_img = img_file.copy()
            thumb_img.thumbnail((thumb_width, thumb_height), Image.ANTIALIAS)

            # save image to django file
            thumb_io = BytesIO()
            thumb_img.save(fp=thumb_io, format='JPEG')
            img.thumb.save(thumb_filename, ContentFile(thumb_io.getvalue()))

            img.save()

        super(AlbumImageModelAdmin, self).save_model(request, obj, form, change)
