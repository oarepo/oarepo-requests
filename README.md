# OARepo Requests

Extensions to Invenio Requests providing workflow-based request handling for repository records.

## Installation

```bash
pip install oarepo-requests
```

## Overview

This library extends Invenio Requests to support workflow-based request handling for repository records. It provides:

- Extended request API with additional endpoints
- Pre-built request types for common curation workflows
- Integration with oarepo-workflows for state transitions
- Action components for extensible request processing
- UI serialization support for request entities

## Features

### Extended Request API

The library extends the standard `/api/requests` endpoint and adds record-specific request endpoints:

- `POST /api/requests` - Create a request with `request_type` and `topic` in payload
- `POST /api/requests/<type>/<topic>` - Create a request via URL parameters
- `GET /api/requests/applicable?topic=<reference>` - List applicable request types for a topic

### Built-in Request Types

#### Publish Requests

**`publish_draft`** - Submit draft for review and publication

- Validates topic is initial version draft
- Supports version field in payload
- Transitions: `submitted` → `published` (accepted) or `draft` (declined)
- Auto-approval when user has curator permissions

**`publish_new_version`** - Publish new version of published record

- For records with existing published versions
- Inherits base publish request behavior

**`publish_changed_metadata`** - Publish metadata changes

- For publishing edited metadata of published records

#### Edit Requests

**`edit_published_record`** - Request to edit published record metadata

- Creates draft from published record
- Requires record to have no existing draft
- Auto-creates draft on acceptance

**`new_version`** - Request to create new version

- Creates new version draft from published record
- Supports `keep_files` parameter (yes/no)
- Only applicable to published records without drafts

#### Delete Requests

**`delete_published_record`** - Request permanent deletion of published record

- Requires `removal_reason` and optional `note` in payload
- Executes record deletion on acceptance
- Marked as dangerous operation

### Request Actions

All request types support standard workflow actions:

- **submit** - Submit created request for approval (transitions to `submitted`)
- **accept** - Accept submitted request (executes request-specific logic)
- **decline** - Decline submitted request (typically returns to previous state)
- **cancel** - Cancel request before acceptance (transitions to `cancelled`)

Custom action implementations:

- `PublishDraftAcceptAction` - Publishes draft, validates no unresolved requests
- `DeletePublishedRecordAcceptAction` - Executes record deletion with metadata preservation
- `EditTopicAcceptAction` - Creates editable draft from published record
- `NewVersionAcceptAction` - Creates new version draft, optionally copies files

### Action Components

The library uses a component architecture for extending action behavior:

```python
class RequestActionComponent:
    def submit(self, identity, action, uow, *args, **kwargs): ...
    def accept(self, identity, action, uow, *args, **kwargs): ...
    def decline(self, identity, action, uow, *args, **kwargs): ...
    def cancel(self, identity, action, uow, *args, **kwargs): ...
```

Built-in components:

**`WorkflowTransitionComponent`** - Applies workflow state transitions based on action outcomes

- Reads transitions from workflow request configuration
- Sets record state according to `status_to` mapping

**`AutoAcceptComponent`** - Auto-accepts requests with auto-approve receivers

- Must be last in component chain
- Executes accept action if receiver has `auto_approve: true`

Configure components in `invenio.cfg`:

```python
REQUESTS_ACTION_COMPONENTS = [
    WorkflowTransitionComponent,
    AutoAcceptComponent,
]
```

### Workflow Integration

Request types integrate with oarepo-workflows through the receiver function:

```python
OAREPO_REQUESTS_DEFAULT_RECEIVER = "oarepo_requests.receiver:default_workflow_receiver_function"
```

The receiver function:

1. Retrieves workflow for the record
2. Looks up request configuration in workflow
3. Evaluates recipient generators to determine receiver
4. Returns entity reference or `None` for auto-approval

Example workflow request configuration:

```python
from oarepo_workflows import WorkflowRequest, WorkflowTransitions, AutoApprove
from oarepo_requests.services.permissions import IfRequestedBy

class MyWorkflowRequests(WorkflowRequestPolicy):
    publish_request = WorkflowRequest(
        requesters=[
            IfInState("draft", then_=[RecordOwners(), CommunityRole("curator")])
        ],
        recipients=[
            IfRequestedBy(
                CommunityRole("curator"),
                then_=[AutoApprove()],
                else_=[CommunityRole("curator")],
            )
        ],
        transitions=WorkflowTransitions(
            submitted="submitted",
            accepted="published",
            declined="draft"
        ),
    )
```

### Permission Generators

**`RequestActive`** - Matches when request action is being executed

- Useful for granting temporary elevated permissions during request processing
- Example: Allow deletion only through request acceptance

```python
class MyWorkflowPermissions(RequestBasedWorkflowPermissions):
    can_delete = [..., RequestActive()]
```

**`IfRequestedBy`** - Conditional generator based on request creator

- Evaluates if creator has specified permissions
- Used in workflow recipient configuration

```python
recipients=[
    IfRequestedBy(
        CommunityRole("curator"),
        then_=[AutoApprove()],
        else_=[CommunityRole("publisher")],
    )
]
```

**`IfNoNewVersionDraft`** - Checks if record has no new version draft

**`IfNoEditDraft`** - Checks if record has no edit draft

### Request Type Properties

Base properties inherited by all request types:

```python
class OARepoRequestType(RequestType):
    dangerous = False              # Marks destructive operations
    allowed_on_draft = True        # Can be created on draft records
    allowed_on_published = True    # Can be created on published records
    editable = None                # Whether request can be edited before submission
    receiver_can_be_none = False   # Whether auto-approval is allowed
    payload_schema = {...}         # Marshmallow schema for request payload
```

Request types also implement:

- `is_applicable_to(identity, topic)` - Check if request type can be used for a topic
- `can_create(identity, data, receiver, topic, creator)` - Validate request creation
- `stateful_name(identity, topic, request)` - Dynamic name based on request state
- `stateful_description(identity, topic, request)` - Dynamic description based on state

### UI Support

The library provides UI serialization for requests:

- Expands entity references (creator, receiver, topic)
- Resolves references using configured entity resolvers
- Includes stateful names and descriptions
- Provides form definitions for request creation

Configuration:

```python
REQUESTS_UI_SERIALIZATION_REFERENCED_FIELDS = ["created_by", "receiver", "topic"]
```

### Configuration

#### Core Settings

```python
# Default receiver function for requests
OAREPO_REQUESTS_DEFAULT_RECEIVER = "oarepo_requests.receiver:default_workflow_receiver_function"

# Allowed receiver entity types
REQUESTS_ALLOWED_RECEIVERS = ["user", "group", "auto_approve"]

# Action components to execute on request actions
REQUESTS_ACTION_COMPONENTS = [
    WorkflowTransitionComponent,
    AutoAcceptComponent,
]

# Request types that trigger publication
PUBLISH_REQUEST_TYPES = ["publish_draft", "publish_new_version"]

# Workflow events configuration
DEFAULT_WORKFLOW_EVENTS = {
    "comment": WorkflowEvent(...),
    "log": WorkflowEvent(...),
}
```

#### Service Configuration

The library overrides Invenio's default request service and resource:

```python
REQUESTS_SERVICE_CLASS = OARepoRequestsService
REQUESTS_SERVICE_CONFIG_CLASS = OARepoRequestsServiceConfig
REQUESTS_RESOURCE_CLASS = OARepoRequestsResource
REQUESTS_RESOURCE_CONFIG_CLASS = OARepoRequestsResourceConfig
```

## Usage

### Creating Requests

Via API:

```bash
# Create request with payload
curl -X POST /api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "request_type": "publish_draft",
    "topic": {"type": "record", "value": "abc123"},
    "payload": {"version": "1.0"}
  }'

# Create request via URL
curl -X POST /api/requests/publish_draft/record:abc123 \
  -H "Content-Type: application/json" \
  -d '{"payload": {"version": "1.0"}}'
```

Via service:

```python
from invenio_requests.proxies import current_requests_service

result = current_requests_service.create(
    identity=identity,
    data={"payload": {"version": "1.0"}},
    request_type="publish_draft",
    topic=record,
)
```

### Executing Actions

```python
from invenio_requests.proxies import current_requests_service

# Submit request
current_requests_service.execute_action(
    identity, request_id, "submit"
)

# Accept request
current_requests_service.execute_action(
    identity, request_id, "accept"
)
```

### Custom Request Types

```python
from oarepo_requests.types.generic import NonDuplicableOARepoRecordRequestType
from oarepo_requests.actions.generic import OARepoAcceptAction

class MyRequestType(NonDuplicableOARepoRecordRequestType):
    type_id = "my_request"
    name = _("My Request")
    description = _("Description of my request")
    
    payload_schema = {
        "my_field": ma.fields.Str(required=True),
    }
    
    @classproperty
    def available_actions(cls):
        return {
            **super().available_actions,
            "accept": MyAcceptAction,
        }

class MyAcceptAction(OARepoAcceptAction):
    name = _("Accept")
    
    def apply(self, identity, uow, *args, **kwargs):
        # Custom acceptance logic
        pass
```

Register via entry point:

```python
[project.entry-points."invenio_requests.types"]
my_request = "myapp.requests:MyRequestType"
```

### Custom Action Components

```python
from oarepo_requests.actions.components import RequestActionComponent

class MyComponent(RequestActionComponent):
    def accept(self, identity, action, uow, *args, **kwargs):
        # Custom logic on accept
        topic = action.topic
        request = action.request
        # ... perform operations
```

Register in `invenio.cfg`:

```python
REQUESTS_ACTION_COMPONENTS = [
    MyComponent,
    WorkflowTransitionComponent,
    AutoAcceptComponent,
]
```

## Architecture

### Request Lifecycle

1. **Creation** - Request created via API or service with validation
2. **Submission** - Request submitted for approval (optional if auto-approved)
3. **Processing** - Receiver accepts or declines request
4. **Completion** - Action logic executes, state transitions applied, components run

### Component Execution Order

For each action execution:

1. Action's `apply()` method executes
2. Parent class action logic executes
3. Each component's action method executes in configured order

Important: Components run after state changes, so they see updated request status.

## Dependencies

- `oarepo-runtime>=2.0.0dev13`
- `oarepo-workflows>=2.0.0dev3`
- `oarepo[rdm]>=14.0.0`
- `oarepo-model>=0.1.0.dev5`

## Development

```bash
# Install with dev dependencies
pip install -e .[dev,tests]

# Run tests
pytest
```

## License

Copyright (c) 2024-2025 CESNET z.s.p.o.

OARepo Requests is free software; you can redistribute it and/or modify it under the terms of the MIT License. See [LICENSE](LICENSE) file for more details.

## Links

- Documentation: <https://github.com/oarepo/oarepo-requests>
- PyPI: <https://pypi.org/project/oarepo-requests/>
- Issues: <https://github.com/oarepo/oarepo-requests/issues>
- OARepo Project: <https://github.com/oarepo>

## Acknowledgments

This project builds upon [Invenio Framework](https://inveniosoftware.org/) and is developed as part of the OARepo ecosystem.
