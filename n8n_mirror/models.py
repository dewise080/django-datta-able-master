from django.db import models

# Create your models here.
from django.db import models


# ---------------------------------------------------------
# Base class for ALL n8n read-only models
# ---------------------------------------------------------
class N8nBase(models.Model):
    class Meta:
        abstract = True
        managed = False
        app_label = "n8n_mirror"


# ---------------------------------------------------------
# workflow_entity
# ---------------------------------------------------------
class WorkflowEntity(N8nBase):
    id = models.CharField(primary_key=True, max_length=36)
    
    name = models.CharField(max_length=128)
    active = models.BooleanField()
    nodes = models.JSONField()
    connections = models.JSONField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    settings = models.JSONField(null=True, blank=True)
    staticData = models.JSONField(null=True, blank=True)
    pinData = models.JSONField(null=True, blank=True)
    versionId = models.CharField(max_length=36)
    triggerCount = models.IntegerField()
    meta = models.JSONField(null=True, blank=True)
    parentFolderId = models.CharField(max_length=36, null=True, blank=True)
    isArchived = models.BooleanField()
    versionCounter = models.IntegerField()
    description = models.TextField(null=True, blank=True)

    class Meta(N8nBase.Meta):
        db_table = "workflow_entity"


# ---------------------------------------------------------
# execution_entity
# ---------------------------------------------------------
class ExecutionEntity(N8nBase):
    id = models.IntegerField(primary_key=True)
    
    finished = models.BooleanField()
    mode = models.CharField(max_length=255)
    retryOf = models.CharField(max_length=255, null=True, blank=True)
    retrySuccessId = models.CharField(max_length=255, null=True, blank=True)
    startedAt = models.DateTimeField(null=True, blank=True)
    stoppedAt = models.DateTimeField(null=True, blank=True)
    waitTill = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=255)
    workflowId = models.CharField(max_length=36)
    deletedAt = models.DateTimeField(null=True, blank=True)
    createdAt = models.DateTimeField()

    class Meta(N8nBase.Meta):
        db_table = "execution_entity"


# ---------------------------------------------------------
# credentials_entity
# ---------------------------------------------------------
class CredentialsEntity(N8nBase):
    id = models.CharField(primary_key=True, max_length=36)
    
    name = models.CharField(max_length=128)
    data = models.TextField()
    type = models.CharField(max_length=128)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    isManaged = models.BooleanField()

    class Meta(N8nBase.Meta):
        db_table = "credentials_entity"


# ---------------------------------------------------------
# user
# ---------------------------------------------------------
class UserEntity(N8nBase):
    id = models.UUIDField(primary_key=True)
    
    email = models.CharField(max_length=255, null=True, blank=True)
    firstName = models.CharField(max_length=32, null=True, blank=True)
    lastName = models.CharField(max_length=32, null=True, blank=True)
    password = models.CharField(max_length=255, null=True, blank=True)
    personalizationAnswers = models.JSONField(null=True, blank=True)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()
    settings = models.JSONField(null=True, blank=True)
    disabled = models.BooleanField()
    mfaEnabled = models.BooleanField()
    mfaSecret = models.TextField(null=True, blank=True)
    mfaRecoveryCodes = models.TextField(null=True, blank=True)
    lastActiveAt = models.DateField(null=True, blank=True)
    roleSlug = models.CharField(max_length=128)

    class Meta(N8nBase.Meta):
        db_table = "user"


# ---------------------------------------------------------
# tag_entity
# ---------------------------------------------------------
class TagEntity(N8nBase):
    id = models.CharField(primary_key=True, max_length=36)
    
    name = models.CharField(max_length=24)
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()

    class Meta(N8nBase.Meta):
        db_table = "tag_entity"


# ---------------------------------------------------------
# shared_workflow
# (composite primary key)
# ---------------------------------------------------------
class SharedWorkflow(N8nBase):
    workflowId = models.CharField(max_length=36)
    projectId = models.CharField(max_length=36)
    
    role = models.TextField()
    createdAt = models.DateTimeField()
    updatedAt = models.DateTimeField()

    class Meta(N8nBase.Meta):
        db_table = "shared_workflow"
        unique_together = (("workflowId", "projectId"),)


# ---------------------------------------------------------
# webhook_entity
# composite PK: webhookPath + method
# ---------------------------------------------------------
class WebhookEntity(N8nBase):
    webhookPath = models.CharField(max_length=255)
    method = models.CharField(max_length=255)

    node = models.CharField(max_length=255)
    webhookId = models.CharField(max_length=255, null=True, blank=True)
    pathLength = models.IntegerField(null=True, blank=True)
    workflowId = models.CharField(max_length=36)

    class Meta(N8nBase.Meta):
        db_table = "webhook_entity"
        unique_together = (("webhookPath", "method"),)
