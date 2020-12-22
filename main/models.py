from django.db import models
from django.urls import reverse
from django.dispatch import Signal
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True,
                                       db_index=True,
                                       verbose_name='passed activation?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Send notification of new comments?')

    class Meta(AbstractUser.Meta):
        pass

    def delete(self, *args, **kwargs):
        for bb in self.bb_set.all():
            bb.delete()
        super().delete(*args, *kwargs)


user_registrated = Signal(providing_args=['instance'])


def user_registrated_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registrated.connect(user_registrated_dispatcher)


class Rubric(models.Model):
    name = models.CharField(
        max_length=20,
        db_index=True,
        unique=True,
        verbose_name='Название',
    )
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Order')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT,
                                     null=True, blank=True, verbose_name='Above category')

    def __str__(self):
        return self.name


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    class Meta:
        proxy = True
        ordering = ('order', 'name', )
        verbose_name = 'Above category'
        verbose_name_plural = 'Above categories'

    def __str__(self):
        return self.name


class SubRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=False)


class SubRubric(Rubric):
    objects = SubRubricManager()

    def __str__(self):
        return f'{self.super_rubric.name} - {self.name}'

    class Meta:
        proxy = True
        ordering = ('super_rubric__order', 'super_rubric__name', 'order', 'name')
        verbose_name = 'Subheading'
        verbose_name_plural = 'Subheadings'


class Bb(models.Model):
    rubric = models.ForeignKey(SubRubric,
                               null=True,
                               on_delete=models.PROTECT,
                               verbose_name='category',
                               related_name='bbs')
    title = models.CharField(max_length=40, verbose_name='product', )
    content = models.TextField(verbose_name='description')
    price = models.FloatField(default=0, verbose_name='price', )
    contacts = models.TextField(verbose_name='Contacts')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='picture')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='the author of the ad')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='display in the list?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='published by')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'ad'
        verbose_name_plural = 'ads'
        ordering = ['-created_at', ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:bb_detail', args=[self.rubric.pk, self.pk, ])


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='ad')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='picture')

    class Meta:
        verbose_name = 'additional illustration'
        verbose_name_plural = 'additional illustrations'


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='ad')
    author = models.CharField(max_length=30, verbose_name='author')
    content = models.TextField(verbose_name='the contents')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Output to the screen?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='published')

    class Meta:
        verbose_name_plural = 'comments'
        verbose_name = 'comment'
        ordering = ['created_at']


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
