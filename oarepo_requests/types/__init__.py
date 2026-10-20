# SPDX-FileCopyrightText: 2024 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""Request types defined in oarepo-requests."""

from __future__ import annotations

from .delete_published_record import DeletePublishedRecordRequestType
from .edit_record import EditPublishedRecordRequestType
from .generic import (
    DefaultReceiverMixin,
    NonDuplicableOARepoRecordRequestType,
    OARepoRequestType,
    RequestTypeWithStatefulName,
    TopicConvertingRequestType,
)
from .publish_changed_metadata import PublishChangedMetadataRequestType
from .publish_draft import PublishDraftRequestType
from .publish_new_version import PublishNewVersionRequestType

__all__ = [
    "DefaultReceiverMixin",
    "DeletePublishedRecordRequestType",
    "EditPublishedRecordRequestType",
    "NonDuplicableOARepoRecordRequestType",
    "OARepoRequestType",
    "PublishChangedMetadataRequestType",
    "PublishDraftRequestType",
    "PublishNewVersionRequestType",
    "RequestTypeWithStatefulName",
    "TopicConvertingRequestType",
]
