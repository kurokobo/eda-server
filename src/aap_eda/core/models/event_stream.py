#  Copyright 2024 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.

from django.db import models

from aap_eda.core.enums import (
    ActivationStatus,
    RestartPolicy,
    RulebookProcessLogLevel,
)
from aap_eda.core.utils import get_default_log_level
from aap_eda.services.activation.engine.common import ContainerableMixin

from .base import UniqueNamedModel
from .mixins import StatusHandlerModelMixin


class EventStream(
    StatusHandlerModelMixin, ContainerableMixin, UniqueNamedModel
):
    """Model representing an event stream."""

    description = models.TextField(default="", blank=True)
    is_enabled = models.BooleanField(default=True)
    decision_environment = models.ForeignKey(
        "DecisionEnvironment",
        on_delete=models.SET_NULL,
        null=True,
    )
    rulebook = models.ForeignKey(
        "Rulebook",
        on_delete=models.SET_NULL,
        null=True,
    )
    extra_var = models.TextField(null=True, blank=True)
    restart_policy = models.TextField(
        choices=RestartPolicy.choices(),
        default=RestartPolicy.ON_FAILURE,
    )
    status = models.TextField(
        choices=ActivationStatus.choices(),
        default=ActivationStatus.PENDING,
    )
    current_job_id = models.TextField(null=True)
    restart_count = models.IntegerField(default=0)
    failure_count = models.IntegerField(default=0)  # internal, since last good
    rulebook_name = models.TextField(
        null=False,
        help_text="Name of the referenced rulebook",
        default="",
    )
    rulebook_rulesets = models.TextField(
        null=False,
        help_text="Content of the last referenced rulebook",
        default="",
    )
    ruleset_stats = models.JSONField(default=dict)
    user = models.ForeignKey("User", on_delete=models.CASCADE, null=False)
    created_at = models.DateTimeField(auto_now_add=True, null=False)
    modified_at = models.DateTimeField(auto_now=True, null=False)
    status_updated_at = models.DateTimeField(null=True)
    status_message = models.TextField(null=True, default=None)
    latest_instance = models.OneToOneField(
        "RulebookProcess",
        null=True,
        default=None,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    channel_name = models.TextField(null=True, default=None)
    source_type = models.TextField(null=False)
    source_args = models.JSONField(null=True, default=None)
    log_level = models.CharField(
        max_length=20,
        choices=RulebookProcessLogLevel.choices(),
        default=get_default_log_level,
    )
    k8s_service_name = models.TextField(
        null=True,
        default=None,
        blank=True,
        help_text="Name of the kubernetes service",
    )

    class Meta:
        db_table = "core_event_stream"
        indexes = [
            models.Index(fields=["name"], name="ix_event_stream_name"),
        ]
        ordering = ("-created_at",)

    def __str__(self) -> str:
        return f"EventStream {self.name} ({self.id})"

    # Implementation of the ContainerableMixin.
    def _get_skip_audit_events(self) -> bool:
        """Event stream skips audit events."""
        return True
