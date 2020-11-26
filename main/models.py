from django.db import models
from django.urls import reverse
from django.dispatch import Signal
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save

from .utilities import send_activation_notification, get_timestamp_path, send_new_comment_notification


class AdvUser(AbstractUser):
    is_activated = models.BooleanField(default=True,
                                       db_index=True,
                                       verbose_name='прошёл активацию?')
    send_messages = models.BooleanField(default=True,
                                        verbose_name='Отправлять оповещение о новых комментариях?')

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
    order = models.SmallIntegerField(default=0, db_index=True, verbose_name='Порядок')
    super_rubric = models.ForeignKey('SuperRubric', on_delete=models.PROTECT,
                                     null=True, blank=True, verbose_name='Надрубрика')


class SuperRubricManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(super_rubric__isnull=True)


class SuperRubric(Rubric):
    objects = SuperRubricManager()

    def __str__(self):
        return self.name

    class Meta:
        proxy = True
        ordering = ('order', 'name', )
        verbose_name = 'Надрубрика'
        verbose_name_plural = 'Надрубрики'


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
        verbose_name = 'Подрубрика'
        verbose_name_plural = 'Подрубрики'


class Bb(models.Model):
    rubric = models.ForeignKey(SubRubric, null=True, on_delete=models.PROTECT, verbose_name='рубрика', related_name='bbs')
    title = models.CharField(max_length=40, verbose_name='товар', )
    content = models.TextField(verbose_name='описание')
    price = models.FloatField(default=0, verbose_name='цена', )
    contacts = models.TextField(verbose_name='Контакты')
    image = models.ImageField(blank=True, upload_to=get_timestamp_path, verbose_name='изображение')
    author = models.ForeignKey(AdvUser, on_delete=models.CASCADE, verbose_name='автор объявления')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='выводить в списке?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='опубликовано')

    def delete(self, *args, **kwargs):
        for ai in self.additionalimage_set.all():
            ai.delete()
        super().delete(*args, **kwargs)

    class Meta:
        verbose_name = 'объявление'
        verbose_name_plural = 'объявления'
        ordering = ['-created_at', ]

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('main:bb_detail', args=[self.rubric.pk, self.pk, ])


class AdditionalImage(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='объявление')
    image = models.ImageField(upload_to=get_timestamp_path, verbose_name='изображение')

    class Meta:
        verbose_name = 'дополнительная иллюстрация'
        verbose_name_plural = 'дополнительные иллюстрации'


class Comment(models.Model):
    bb = models.ForeignKey(Bb, on_delete=models.CASCADE, verbose_name='объявление')
    author = models.CharField(max_length=30, verbose_name='автор')
    content = models.TextField(verbose_name='содержание')
    is_active = models.BooleanField(default=True, db_index=True, verbose_name='Выводить на экран?')
    created_at = models.DateTimeField(auto_now_add=True, db_index=True, verbose_name='опубликован')

    class Meta:
        verbose_name_plural = 'комментарии'
        verbose_name = 'комментарий'
        ordering = ['created_at']


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bb.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
