from django.contrib import admin
import datetime

from django.urls import reverse
from django.utils.html import format_html
from django.utils.http import urlencode
from django.utils.safestring import mark_safe

from .models import AdvUser, SuperRubric, SubRubric, Bb, AdditionalImage, Comment
from .utilities import send_activation_notification
from .forms import SubRubricForm


def send_activation_notifications(modeladmin, request, queryset):
    for rec in queryset:
        if not rec.is_activated:
            send_activation_notification(rec)
    modeladmin.message_user(request, 'Notification emails sent')


send_activation_notifications.short_description = 'Sending emails with activation notifications'


class NonactivatedFilter(admin.SimpleListFilter):
    title = 'Went through the activation?'
    parameter_name = 'actstate'

    def lookups(self, request, model_admin):
        return (
            ('activated', 'Passed'),
            ('threedays', 'Not more than three days have passed'),
            ('week', 'Not more than a week has passed'),
        )

    def queryset(self, request, queryset):
        val = self.value()
        if val == 'activated':
            return queryset.filter(is_active=True, is_activated=True)
        elif val == 'threedays':
            d = datetime.date.today() - datetime.timedelta(days=3)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)
        elif val == 'week':
            d = datetime.date.today() - datetime.timedelta(weeks=1)
            return queryset.filter(is_active=False, is_activated=False, date_joined__date__lt=d)


class AdvUserAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_activated', 'date_joined', 'bb_link')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = (NonactivatedFilter, )
    fields = (
        ('username', 'email', ),
        ('first_name', 'last_name'),
        ('send_messages', 'is_active', 'is_activated'),
        ('is_staff', 'is_superuser'),
        'groups', 'user_permissions',
        ('last_login', 'date_joined')
    )
    readonly_fields = ('last_login', 'date_joined')
    actions = (send_activation_notifications, )

    def bb_link(self, obj):
        count = obj.bb_set.count()
        url = (
                reverse("admin:main_bb_changelist")
                + "?"
                + urlencode({"author__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Ads: {}</a>', url, count)

    bb_link.short_description = 'Ads'


class AdditionalImageInline(admin.TabularInline):
    model = AdditionalImage
    extra = 1


class CommentInline(admin.TabularInline):
    model = Comment
    extra = 1


@admin.register(Bb)
class BbAdmin(admin.ModelAdmin):
    list_display = (
        'rubric', 'title', 'content',
        'author', 'price', 'created_at',
        'comment_count', "view_comments_link")
    fields = (
        ('rubric', 'author'),
        'title', 'content', 'price',
        'contacts', 'image', 'is_active'
    )
    list_filter = ('created_at', 'rubric')
    search_fields = ('title', 'content', )
    inlines = (CommentInline, AdditionalImageInline)

    def comment_count(self, obj):
        return obj.comment_set.count()

    comment_count.short_description = 'Comments'

    def view_comments_link(self, obj):
        count = obj.comment_set.count()
        url = (
                reverse("admin:main_comment_changelist")
                + "?"
                + urlencode({"bb__id": f"{obj .id}"})
        )
        return format_html('<a href="{}">{} Comments</a>', url, count)

    view_comments_link.short_description = "Comments"


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric', )
    inlines = (SubRubricInline, )


class SubRubricAdmin(admin.ModelAdmin):
    list_display = ('name', 'bb_link')
    list_filter = ('super_rubric',)
    form = SubRubricForm

    def bb_link(self, obj):
        count = obj.bb_set.count()
        url = (
                reverse("admin:main_bb_changelist")
                + "?"
                + urlencode({"rubric__id": f"{obj.id}"})
        )
        return format_html('<a href="{}">Ads: {}</a>', url, count)

    bb_link.short_description = 'Ads'


admin.site.register(SuperRubric, SuperRubricAdmin)
admin.site.register(SubRubric, SubRubricAdmin)
admin.site.register(AdvUser, AdvUserAdmin)


class CommentAdmin(admin.ModelAdmin):
    list_display = ('author', 'content', 'created_at', 'is_active', 'bb_title', )
    list_display_links = ('author', 'content',)
    list_filter = ('is_active', 'author', 'created_at', )
    search_fields = ('author', 'content',)
    date_hierarchy = 'created_at'
    fields = ('bb', 'author', 'content', 'is_active', 'created_at')
    readonly_fields = ('created_at',)

    def bb_title(self, obj):
        title = obj.bb.title
        url = (
                reverse("admin:main_bb_change", args=[obj.bb.id])
        )
        return format_html('<a href="{}">Ad: {}</a>', url, title)

    bb_title.short_description = 'Ad'


admin.site.register(Comment, CommentAdmin)
