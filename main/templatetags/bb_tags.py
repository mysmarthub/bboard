from django import template
from django.db.models import Count

from ..models import Bb, SubRubric, SuperRubric, Rubric

register = template.Library()


# @register.inclusion_tag('main/new_bb.html')
# def get_new_bb(count=5):
#     bbs = Bb.objects.order_by('-published')[:count]
#     context = {
#         'bbs': bbs,
#     }
#     return context


@register.simple_tag
def total_super_rubric():
    return SuperRubric.objects.count()


@register.simple_tag
def total_sub_rubric():
    return SubRubric.objects.count()


@register.simple_tag
def total_bb():
    return Bb.objects.count()


@register.simple_tag
def total_bb_rubric(rubric):
    return rubric.bbs.count()


@register.simple_tag
def total_user_bb(user):
    return Bb.objects.filter(author=user).count()
