from django import template

from ..models import Bb, SubRubric, SuperRubric

register = template.Library()


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
