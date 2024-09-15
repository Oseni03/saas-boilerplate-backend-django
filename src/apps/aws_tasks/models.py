import hashid_field
from django.db import models
from django.utils.translation import gettext_lazy as _

from . import managers


# Create your models here.
class StateChoice(models.TextChoices):
    PENDING = "PENDING", _("Pending")
    RECEIVED = "RECEIVED", _("Received")
    STARTED = "STARTED", _("Started")
    SUCCESS = "SUCCESS", _("Success")
    FAILURE = "FAILURE", _("Failure")
    REVOKED = "REVOKED", _("Revoked")
    REJECTED = "REJECTED", _("Rejected")
    RETRY = "RETRY", _("Retry")
    IGNORED = "IGNORED", _("Ignored")


class TaskResult(models.Model):
    """Task result/status."""

    id: str = hashid_field.HashidAutoField(primary_key=True)
    task_name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name=_("Task Name"),
        help_text=_("Name of the Task which was run"),
    )
    task_args = models.JSONField(
        null=True,
        verbose_name=_("Task Positional Arguments"),
        help_text=_(
            "JSON representation of the positional arguments " "used with the task"
        ),
    )
    task_kwargs = models.JSONField(
        null=True,
        verbose_name=_("Task Named Arguments"),
        help_text=_("JSON representation of the named arguments " "used with the task"),
    )
    status = models.CharField(
        max_length=50,
        default=StateChoice.PENDING,
        choices=StateChoice.choices,
        verbose_name=_("Task State"),
        help_text=_("Current state of the task being run"),
    )
    result = models.JSONField(
        null=True,
        default=None,
        editable=False,
        verbose_name=_("Result Data"),
        help_text=_(
            "The data returned by the task.  "
            "Use content_encoding and content_type fields to read."
        ),
    )
    date_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created DateTime"),
        help_text=_("Datetime field when the task result was created in UTC"),
    )
    date_done = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Completed DateTime"),
        help_text=_("Datetime field when the task was completed in UTC"),
    )
    traceback = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Traceback"),
        help_text=_("Text of the traceback if the task generated one"),
    )

    objects = managers.TaskResultManager()

    class Meta:
        """Table information."""

        ordering = ["-date_done"]

        verbose_name = _("task result")
        verbose_name_plural = _("task results")

        # Explicit names to solve https://code.djangoproject.com/ticket/33483
        indexes = [
            models.Index(fields=["task_name"], name="aws_lambda_task_na_08aec9_idx"),
            models.Index(fields=["status"], name="aws_lambda_status_9b6201_idx"),
            models.Index(fields=["date_created"], name="aws_lambda_date_cr_f04a50_idx"),
            models.Index(fields=["date_done"], name="aws_lambda_date_do_f59aad_idx"),
        ]

    def as_dict(self):
        return {
            "task_id": self.id,
            "task_name": self.task_name,
            "task_args": self.task_args,
            "task_kwargs": self.task_kwargs,
            "status": self.status,
            "result": self.result,
            "date_done": self.date_done,
            "traceback": self.traceback,
        }

    def __str__(self):
        return "<Task: {0.task_id} ({0.status})>".format(self)
