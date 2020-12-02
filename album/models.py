#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import uuid
from django.db import models
from django.dispatch.dispatcher import receiver


class Album(models.Model):
    PHOTOGRAPH = 0
    AWESOME = 1
    GALLERY = 2

    CATE_ITEMS = (
        (PHOTOGRAPH, 'photograph'),
        (AWESOME, 'awesome photograph'),
        (GALLERY, 'gallery'),
    )

    CATE_MAP = {"photograph": PHOTOGRAPH, "awesome": AWESOME, "gallery": GALLERY}

    category = models.PositiveIntegerField(default=GALLERY, choices=CATE_ITEMS, verbose_name="Category")
    title = models.CharField(max_length=70)
    desc = models.TextField(max_length=1024)
    thumb = models.ImageField(upload_to='covers', blank=False)
    tags = models.CharField(max_length=250)
    is_visible = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)
    modified = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=50, unique=True)

    # def get_absolute_url(self):
    #    return reverse('album', kwargs={'slug':self.slug})

    def __unicode__(self):
        return self.title

    # display album name rather than "object" in the drop-down list.
    def __str__(self):
        return self.title


@receiver(models.signals.post_delete, sender=Album)
def auto_delete_album_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.thumb:
        if os.path.isfile(instance.thumb.path):
            os.remove(instance.thumb.path)


@receiver(models.signals.pre_save, sender=Album)
def auto_delete_album_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = Album.objects.get(pk=instance.pk).thumb
    except Album.DoesNotExist:
        return False

    new_file = instance.thumb
    if old_file != new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)


class AlbumImage(models.Model):
    image = models.ImageField(max_length=50, upload_to='albums', blank=False)
    thumb = models.ImageField(max_length=50, upload_to='albums', blank=True)
    desc = models.CharField(max_length=300, default="The author is so lazy that leave nothing!", blank=False)
    like_num = models.PositiveIntegerField(default=0, blank=False, verbose_name='like number')

    width = models.IntegerField(default=0)
    height = models.IntegerField(default=0)

    album = models.ForeignKey('album', on_delete=models.PROTECT)
    alt = models.CharField(max_length=255, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=70, default=uuid.uuid4, editable=False)


@receiver(models.signals.post_delete, sender=AlbumImage)
def auto_delete_image_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

    if instance.thumb:
        if os.path.isfile(instance.thumb.path):
            os.remove(instance.thumb.path)


#@receiver(models.signals.pre_save, sender=AlbumImage)
#def auto_delete_image_file_on_save(sender, instance, **kwargs):
#    """
#    Deletes old file from filesystem
#    when corresponding `MediaFile` object is updated
#    with new file.
#    """
#    if not instance.pk:
#        return False
#
#    try:
#        old_image = AlbumImage.objects.get(pk=instance.pk).image
#        old_thumb = AlbumImage.objects.get(pk=instance.pk).thumb
#    except AlbumImage.DoesNotExist:
#        return False
#
#    new_image = instance.image
#    new_thumb = instance.thumb
#    if old_image != new_image:
#        if os.path.isfile(old_image.path):
#            os.remove(old_image.path)
#
#    if old_thumb != new_thumb:
#        if os.path.isfile(old_thumb.path):
#            os.remove(old_thumb.path)
