# -*- coding: utf-8 -*-
"""
This module provides utility models for the entire project
"""
from __future__ import absolute_import
import copy
from django.contrib import admin
from django.contrib.staticfiles.storage import staticfiles_storage
from django.db.models import Model, Q, DateTimeField, ForeignKey, PROTECT, BooleanField
from django.http import HttpResponse
from django.utils import timezone
# from django.utils.translation import ugettext_lazy as _
from django.contrib.auth import get_user_model
User = get_user_model()


class AdminStaticMixin(admin.ModelAdmin):
    """This class provides Admin site objects with static media mixins.
    """

    class Media:
        js = ()
        css = {}


# class QQ:
#     def __xor__(self, other):
#         """Fake XOR implementation to return either the first or second.

#         Returns the first condition if it is true, otherwise checks the second
#         condition if and only if the first condition is not true.

#         A real XOR would `check self._combine(not_other, self.AND)`, followed
#         by `not_self._combine(other, self.AND)`.  This checks
#         `not_self._combine(other, self.AND)` followed by
#         `self._combine(self, self,AND)`
#         """
#         not_self = ~copy.deepcopy(self)

#         x = self._combine(self, self.AND)
#         y = not_self._combine(other, self.AND)

#         return y | x

# Q.__bases__ += (QQ,)


class MetaModel(Model):
    _active = BooleanField(default=True, verbose_name="Is Active")
    _created = DateTimeField(auto_now_add=True, verbose_name="Datetime Created")
    _last_updated = DateTimeField(auto_now=True, verbose_name="Datetime Updated")
    _last_updated_by = ForeignKey(
        User,
        on_delete=PROTECT,
        blank=True,
        null=True,
        verbose_name="Last Updated By",
        related_name="%(class)s_last_updated_by"
    )
    _created_by = ForeignKey(
        User,
        on_delete=PROTECT,
        blank=True,
        null=True,
        verbose_name="Created By",
        related_name="%(class)s_created_by"
    )
    class Meta:
        abstract = True

def set_meta_fields(request, obj, form, change, inline=False):
    if form.has_changed() or inline:
        if form.changed_data or inline:
            obj._last_updated_by = request.user
            obj._updated = timezone.now()
        if not obj.pk:
            obj._created_by = request.user

    return obj