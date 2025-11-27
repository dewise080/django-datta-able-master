from django.contrib import admin

from . import models


class ReadOnlyAdminMixin:
    """Mixin that disables create/update/delete operations in the admin."""

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        return [field.name for field in self.model._meta.fields]

    actions = None


@admin.register(models.WorkflowEntity)
class WorkflowAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "active", "isArchived", "triggerCount", "createdAt", "updatedAt")
    search_fields = ("id", "name", "description")
    list_filter = ("active", "isArchived")
    ordering = ("-updatedAt",)


@admin.register(models.ExecutionEntity)
class ExecutionAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "workflowId", "status", "mode", "finished", "startedAt", "stoppedAt", "createdAt")
    search_fields = ("id", "workflowId", "status", "mode")
    list_filter = ("status", "finished", "mode")
    ordering = ("-createdAt",)


@admin.register(models.CredentialsEntity)
class CredentialsAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "type", "isManaged", "createdAt", "updatedAt")
    search_fields = ("id", "name", "type")
    list_filter = ("type", "isManaged")
    ordering = ("-updatedAt",)


@admin.register(models.UserEntity)
class UserAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "email", "firstName", "lastName", "roleSlug", "disabled", "mfaEnabled", "createdAt", "lastActiveAt")
    search_fields = ("id", "email", "firstName", "lastName")
    list_filter = ("roleSlug", "disabled", "mfaEnabled")
    ordering = ("-createdAt",)


@admin.register(models.TagEntity)
class TagAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "createdAt", "updatedAt")
    search_fields = ("id", "name")
    ordering = ("-updatedAt",)


@admin.register(models.SharedWorkflow)
class SharedWorkflowAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("workflowId", "projectId", "role", "createdAt", "updatedAt")
    search_fields = ("workflowId", "projectId", "role")
    ordering = ("-updatedAt",)


@admin.register(models.WebhookEntity)
class WebhookAdmin(ReadOnlyAdminMixin, admin.ModelAdmin):
    list_display = ("webhookPath", "method", "workflowId", "node", "pathLength")
    search_fields = ("webhookPath", "method", "workflowId", "node")
    list_filter = ("method",)
    ordering = ("webhookPath",)
