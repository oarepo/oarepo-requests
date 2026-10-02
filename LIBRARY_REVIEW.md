# Additional library review

Reviewed on 2026-09-22 against local `main` (`f19a9200`) and
`library-review-ps1` (`213cb06d`), including the inline `REVIEW` comments and the
existing working-tree edits. This report is committed on a branch from
`library-review-ps1`; it contains suggestions, not implemented fixes.

The findings below come from static source tracing, including the installed
Invenio dependencies and the local `oarepo-workflows` sources. Tests were not run,
as required by `/home/ron/prace/AGENTS.md` for code reviews. The validation cases
are proposed regression tests, not claims of successful reproduction. P1 means
high priority; P2 means normal priority; P3 means minor.

## Regression reproducers

[tests/test_requests/test_review_regressions.py](tests/test_requests/test_review_regressions.py)
contains 16 numbered tests (21 parametrized cases). Tests 01--13 correspond to
the numbered findings below; 14--16 cover the three smaller issues in order.
Each asserts the intended behavior, so unfixed bugs produce ordinary test
failures rather than expected-failure marks. The `keep_files=no` and new-format
topic cases are working controls.

The transaction, persistence, and pagination cases use the existing app,
database, search, and record fixtures. Pagination uses a one-result page so only
two historical records are needed. Notification task dispatch is disabled in
this module; notification-generator/filter tests exercise their code directly.

Run the reproducers with the standard runner:

```bash
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://invenio:invenio@localhost:5432/invenio \
  ./run.sh test tests/test_requests/test_review_regressions.py -q
```

Add `-k review_02` to run just the deletion rollback reproducer, for example.
The current working tree contains the resource-config `fields` import fix
mentioned below; a clean checkout also needs that fix to get past app imports.
The tests have been syntax-checked and passed file-scoped Ruff lint/format
checks, but have not been executed, following the workspace's review instruction.

## 1. [P1, branch regression] New-version publication disappears from applicable requests

Location: [types/publish_new_version.py:90](oarepo_requests/types/publish_new_version.py#L90).

The refactor replaces the `topic_type()` method with `get_topic_type()` and adds
`topic_type = "new_version"`, but the subclass still calls `cls.topic_type(topic)`.
For a valid new-version draft this raises `TypeError: 'str' object is not
callable`. `WorkflowRequest.is_applicable()` catches that exception and returns
false, so the publication request disappears from applicable-request responses
and expanded record actions. Direct calls to `is_applicable_to()` raise instead.

**Suggestion:** remove the redundant subclass `is_applicable_to()` override and
use the new base implementation, which already compares against `cls.topic_type`.

**Validation:** create a new-version draft and assert that both the applicable
endpoint and expanded draft include `publish_new_version`; also call the type's
applicability method directly. The added expansion test only covers an initial
draft and misses this regression.

## 2. [P1, existing] Deletion commits before acceptance succeeds

Location: [actions/delete_published_record.py:90](oarepo_requests/actions/delete_published_record.py#L90).

`delete_record()` is called without the enclosing `uow`, and the action then
explicitly calls `db.session.commit()`. Invenio's `unit_of_work` decorator creates
and commits a separate unit of work when none is supplied. Consequently, the
record's deletion is committed before `OARepoGenericActionMixin.execute()` runs
the base acceptance action and the workflow components. A later exception can
leave the record deleted while the request remains submitted. A retry can then
fail because the record is already deleted. Removing only the explicit commit
does not fix the independently committed service call.

**Suggestion:** pass `uow=uow` to `delete_record()` and remove the explicit session
commit. Keep the returned topic for subsequent components.

**Validation:** inject a failure after deletion but before acceptance completes;
reload using a fresh database session and verify that both deletion status and
request status rolled back. Also verify the normal successful deletion path.

## 3. [P1, existing] Keeping files during version creation breaks rollback

Location: [actions/new_version.py:44](oarepo_requests/actions/new_version.py#L44).

`new_version()` joins the request's unit of work, but the following
`import_files()` call does not. For `payload.keep_files == "yes"`, the decorated
file import creates its own unit of work and commits the shared database session,
including the new draft already flushed by `new_version()`. If acceptance or a
later component fails, the draft and imported files can survive the request's
rollback; the outer unit's indexing operations may never run.

**Suggestion:** call `topic_service.import_files(identity, new_version_topic.id,
uow=uow)` so that draft creation, file import, and acceptance share one commit.

**Validation:** inject a failure in a later accept component with `keep_files=yes`.
Verify that no new draft, next-version pointer, or imported file association
survives. Repeat with `keep_files=no` to cover both paths. Existing file-copy tests
check successful requests, not rollback.

## 4. [P1, existing] Publication can bypass unresolved requests beyond page one

Locations: [types/publish_base.py:123](oarepo_requests/types/publish_base.py#L123)
and [actions/publish_draft.py:119](oarepo_requests/actions/publish_draft.py#L119).

Both guards call `search_requests()` and iterate the returned `_results`.
That helper uses the paginated `RequestsService.search()` API with its default
page size, and includes closed requests as well as open ones. A blocking request
outside the first page is never examined. The database status recheck only
protects hits that were returned; it cannot recover omitted hits. Both creation
and acceptance can therefore allow publication with unresolved requests.

**Suggestion:** make the blocking-request check exhaustive and authoritative.
Prefer a database query for the topic's active requests. Scanning all matching
search hits is a useful pagination fix, but still needs a strategy for requests
that have not reached the index. Share the check between creation and acceptance
and preserve the intended exclusions for publication requests.

**Validation:** create more than one page of request history, place an open
non-publication request after the first page, and assert that creation and
acceptance both reject publication. Include a request created in the same unit
of work and not yet indexed.

## 5. [P1, existing] Non-duplicable requests can be duplicated within one transaction

Locations: [utils.py:146](oarepo_requests/utils.py#L146),
[types/generic.py](oarepo_requests/types/generic.py) (`NonDuplicableOARepoRecordRequestType.can_create`),
and [services/oarepo/service.py:142](oarepo_requests/services/oarepo/service.py#L142).

The uniqueness check consults only OpenSearch. Indexing and `IndexRefreshOp` run
after the enclosing database transaction commits. Two creations of the same
non-duplicable type and topic inside one supplied unit of work therefore both see
no indexed request and can both succeed. Concurrent transactions have the same
race. The installed `RequestMetadata` has no uniqueness constraint for open
requests by topic and type; distinct UUIDs/request numbers do not prevent this.

**Suggestion:** enforce this invariant transactionally using a database-backed
check and appropriate serialization, such as a topic/type lock or a suitable
uniqueness constraint. A database check without concurrency protection, or a
larger search page, is insufficient. Keep search-based checks for presentation
only if desired.

**Validation:** attempt two creations in a shared unit of work, then repeat from
two database sessions synchronized before the check. Exactly one open request
should persist. Verify that a closed request allows a later replacement.

## 6. [P2, existing] Editing an older published version selects the wrong publication type

Location: [types/publish_base.py:170](oarepo_requests/types/publish_base.py#L170).

`get_topic_type()` uses `versions.is_latest` to distinguish an unpublished version
from a metadata edit. In Invenio, that flag means the record ID equals the latest
published version ID. An edit draft of an older published version is therefore
not latest even though it is already published: version 1 is classified as
`initial`, and older versions above 1 as `new_version`. This hides the metadata
publication request and can select a different workflow/recipient policy.

**Suggestion:** after checking `is_draft`, use `is_published` to recognize edits
of existing published versions. Use the version index to distinguish initial
and new-version drafts only for drafts that have never been published.

**Validation:** publish versions 1, 2, and 3, then edit versions 1 and 2. Both
must classify as metadata edits; a fresh version 4 draft must remain a
new-version draft. The installed draft service supports editing by record ID
without requiring that version to be latest.

## 7. [P2, existing] A requested version label is lost when submission has no state transition

Location: [actions/publish_draft.py:99](oarepo_requests/actions/publish_draft.py#L99).

The submit action changes `self.topic.metadata["version"]` but does not register
a record commit. The usual `submitted` workflow transition happens to persist
the topic through `StateChangeOperation`. With the supported default
`WorkflowTransitions()` or `submitted=None`, no such operation occurs. Acceptance
resolves a fresh draft; initial-draft acceptance does not reapply the version
payload, so the published record can lose the requested label. The special
new-version accept action already registers an explicit commit, which masks this
issue on that path.

**Suggestion:** register a `RecordCommitOp` in the shared unit of work whenever
submission changes topic metadata, independently of workflow transitions.

**Validation:** submit an initial publication request with a version payload and
no submitted transition. Read the draft in a fresh session, accept the request,
and verify the version on the published record. Cover manual and auto-acceptance.

## 8. [P2, existing] Explicit creators crash conditional recipient selection

Location: [services/permissions/generators/conditional.py:60](oarepo_requests/services/permissions/generators/conditional.py#L60).

`IfRequestedBy` accepts identities, entity proxies, and other creator forms.
For an explicit user object or reference dictionary it calls
`ResolverRegistry.reference_entity()`, which returns a dictionary, then calls
`creator.get_needs()` on that dictionary. Creating a request on behalf of another
user thus raises `AttributeError` when the workflow uses this generator. Existing
conditional-recipient tests use the implicit identity branch only.

**Suggestion:** turn a reference dictionary into an entity proxy with
`resolve_entity_proxy(..., raise_=True)` before reading its needs. For a concrete
entity, obtain its reference first. Preserve the identity and proxy fast paths.

**Validation:** exercise equivalent creators supplied as an `Identity`, user
entity, `{"user": id}` reference, and entity proxy; all should select the same
recipient branch. An unresolvable reference should raise a controlled error.

## 9. [P2, existing] Explicit expiration is silently discarded

Location: [services/oarepo/service.py:132](oarepo_requests/services/oarepo/service.py#L132).

The override accepts `expires_at` but omits it from `super().create()`.
The upstream service defaults it to `None` and passes it to request creation,
so a caller-supplied deadline is not persisted. Such requests do not expire at
the requested time. The override also discards additional keyword context
instead of forwarding it to the upstream permission check.

**Suggestion:** forward `expires_at=expires_at` and supported keyword context.
Keep permission checks consistent about that context, including any preliminary
`can_create()` check.

**Validation:** create a request with an explicit future deadline, reload it,
and verify the stored deadline and expiration behavior. Include a custom
permission policy that consumes the forwarded context.

## 10. [P2, existing] Receiver selection uses the unconverted topic and unvalidated payload

Location: [services/oarepo/service.py:106](oarepo_requests/services/oarepo/service.py#L106).

The default receiver is selected before schema loading and before
`convert_topic()`. For `publish_changed_metadata` created through a published
record reference, recipient generators inspect the published record while the
request's creation checks operate on the edit draft. If recipients depend on
state or changed metadata, the request can go to the wrong reviewer or take an
auto-approval branch intended for different record data. Likewise, a payload
generator sees raw input without schema defaults/coercion.

**Suggestion:** define and consistently use the canonical topic and validated
payload for recipient selection and creation. Move normalization before default
receiver resolution, preserving any explicit-receiver behavior intentionally
supported by the service.

**Validation:** configure different recipients for the published and draft
metadata/state, then create the same metadata-publication request through each
topic form. Both should select the draft's recipient. Also cover a recipient
decision that uses a schema-defaulted payload value.

## 11. [P2, existing] Notifications fail for allowed requests without a receiver

Locations: [notifications/generators/context.py:49](oarepo_requests/notifications/generators/context.py#L49)
and [notifications/generators/recipients.py:39](oarepo_requests/notifications/generators/recipients.py#L39).

`ReferenceSavingEntityResolve` deliberately skips `None`, so no
`request.receiver` reference is saved. `EntityRecipientGenerator` then
unconditionally looks up that saved reference and raises `KeyError`.
`GeneralRequestParticipantsRecipient` always invokes this generator for the
receiver, so a comment on a receiver-less request aborts notification processing,
including delivery to otherwise valid creators/commenters. Publish submission
builders also invoke it directly. Receiver-less requests are explicitly allowed
by several types and covered by creation tests.

**Suggestion:** treat an absent optional receiver as contributing zero
recipients, while retaining useful errors for malformed non-null references.

**Validation:** process a comment notification for a receiver-less request and
verify delivery to eligible remaining participants. Also process a submission
notification with no receiver and ensure it completes with no recipients.

## 12. [P2, existing] Existing search documents cannot be loaded after installing the topic dumper

Location: [records/dumpers.py:37](oarepo_requests/records/dumpers.py#L37).

The extension writes topic references as arrays and unconditionally loads them
with `data["topic"][0]`. Upstream/older indexed requests contain a topic dictionary,
such as `{"record": "pid"}` or `{"group": "name"}`. On an existing index, loading
any such hit raises `KeyError: 0`. The extension is installed globally on the
request dumper, and the request index name/schema version is unchanged. Search
serialization calls `Request.loads()` for every hit, so one old document can
break the whole response until it is reindexed.

**Suggestion:** accept both the old dictionary representation and the new array
representation during loading. Define behavior for absent/null topics and
malformed arrays as well. Document reindexing if the additional model reference
is needed for filtering existing documents.

**Validation:** load both document formats and serialize a mixed search page.
Verify that the canonical request topic remains a single reference dictionary.

## 13. [P2, existing] Version-label uniqueness only covers the first page of versions

Locations: [types/publish_new_version.py:75](oarepo_requests/types/publish_new_version.py#L75)
and [actions/publish_draft.py:92](oarepo_requests/actions/publish_draft.py#L92).

Both checks iterate `search_versions(...).to_dict()["hits"]["hits"]`, which is a
single page. A label belonging to an older version beyond that page is accepted
at both creation and submission. This violates the explicit uniqueness check
without needing concurrent requests.

**Suggestion:** use an exhaustive version lookup or an authoritative existence
query scoped to the record family and exact label. If search is retained, handle
index freshness and the intended visibility of restricted versions as well.

**Validation:** create more published versions than the configured page size,
then request a label from a version outside page one. Creation and submission
must both reject it; a fresh label must succeed.

## Smaller concrete issues

- **[P2, existing] False filters still filter.** In
  [services/facets/params.py](oarepo_requests/services/facets/params.py), both
  `RequestOwnerFilterParam` and `RequestNotOwnerFilterParam` test
  `value is not None`. Consequently, `mine=false` and `assigned=false` activate
  their filters just like `true`; sending both false can yield contradictory
  filters and no results. Define the false case explicitly, normally as no
  additional filter, and cover omitted/true/false parameters.
- **[P2, existing] The no-email recipient filter has no effect.**
  [notifications/filters.py](oarepo_requests/notifications/filters.py)
  (`UsersWithNoMailRecipientFilter`) returns a new dictionary, but Invenio's
  `NotificationBuilder.filter_recipients()` ignores filter return values and
  expects in-place mutation. Remove unwanted entries from the supplied dictionary;
  define how `email_hidden` and empty addresses should be handled. Validate via
  `builder.filter_recipients()`, not just the filter's return value.
- **[P3, branch regression] The invalid-topic error reports a boolean.** In
  [types/publish_base.py:83](oarepo_requests/types/publish_base.py#L83), the walrus
  expression assigns the result of `!=`, so the error reads `Topic type True`.
  Assign the topic type separately or parenthesize the assignment before comparing.

## Relationship to the existing review comments

- The runtime `fields` import needed by the relocated search-argument schema is
  already fixed in the user's uncommitted resource-config edit. The committed
  source branch alone still has that import-time failure; this review does not
  claim the existing fix as new work or include it in the report commit.
- `REQUESTS_ALLOWED_RECEIVERS` is used by `OARepoRequestType.allowed_receiver_ref_types`.
  `DEFAULT_WORKFLOW_EVENTS` is consumed by `oarepo-workflows`. Those settings are
  not dead merely because their uses cross package boundaries.
- `payload.created_topic` is written by `NewVersionAcceptAction`; its expandable
  field remains relevant. The existing new-version tests also exercise it.
- The existing comments already identify topic-less creation, non-workflow topics
  entering workflow components, and published-versus-draft title resolution.
  The findings above focus on additional failures rather than repeating those
  comments as newly discovered issues.
- `RequestEntityResolve` returning a dictionary in its title-present branch is
  inconsistent with its other return path, but the installed notification builder
  ignores context-generator return values. It is not listed as a demonstrated
  notification-pipeline crash.

Suggested implementation order: fix the applicability regression and both
transaction boundaries first, then make publication blockers and duplicate
prevention authoritative, followed by the remaining routing, persistence,
notification, and compatibility fixes.

# Follow-up review (2026-10-01)

Second pass against `library-review-ps1-deeper-review` (`eb5e18cf`) plus the
uncommitted working tree. It covers the branch's fixes for the findings above,
all inline `REVIEW` comments, and the whole package traced into the installed
Invenio and oarepo dependencies. No reproducer tests were added for this pass;
the **Validation** paragraphs describe proposed tests.

Two items were confirmed by running code: N1 with a temporary test (removed
afterwards) and B1 with a standalone script. The root cause of N2 was confirmed
with a marshmallow snippet. Everything else comes from static tracing.

B-items concern the branch's own changes. N-items are pre-existing issues not
mentioned above or in the inline comments.

## Status of the branch's fixes

### B1. [P2, branch] The fix for finding 11 is ineffective

Locations: [notifications/generators/context.py:41](oarepo_requests/notifications/generators/context.py#L41)
and [notifications/generators/recipients.py:40](oarepo_requests/notifications/generators/recipients.py#L40).

`EntityRecipientGenerator` now returns early when `get_reference_type()` yields
`None`. However, `get_reference_type()` indexes `self.references[key]`, which
raises `KeyError` whenever `ReferenceSavingEntityResolve` skipped a null
receiver, so the guard is never reached. A standalone run raised
`KeyError: 'request.receiver'`; `test_review_11` still fails.

**Suggestion:** make `get_reference_type()` return `None` for an unknown key
(`self.references.get(key)`) and keep the guard.

### B2. [P2, branch] Finding 8 is still open

Location: [services/permissions/generators/conditional.py:56](oarepo_requests/services/permissions/generators/conditional.py#L56).

The change narrows the `creator` annotation to `Identity | EntityProxy`, but
`OARepoRequestsService.create()` still forwards reference dictionaries and
entities unchanged. Both reach `.get_needs()` and raise `AttributeError`, so
`test_review_08` still fails. The suggestion under finding 8 still applies.

### B3. [P2, branch] `scan()` in `search_requests` changes record expansion

Locations: [utils.py:341](oarepo_requests/utils.py#L341) and
[services/components/results.py:57](oarepo_requests/services/components/results.py#L57).

Switching to `scan()` makes the publication guards exhaustive, which is part of
finding 4. However, `RequestsComponent` uses the same helper. Every `?expand`
read of a record now serializes all historical requests of that record:

- in `_doc` order instead of newest first;
- each with full link rendering, which is expensive (see N1);
- through a new scroll context on each read.

**Suggestion:** keep `scan()` for the guards, which only read raw hits, and use
a sorted, paginated `search()` for expansion, through two separate helpers.

**Validation:** create more than one page of requests on a record, read it with
`expand`, and assert that the list is bounded and ordered newest first.

### B4. [P3, branch] Cancelling a publish request converts the topic before elevation

Locations: [types/publish_base.py:67](oarepo_requests/types/publish_base.py#L67),
[actions/publish_draft.py:56](oarepo_requests/actions/publish_draft.py#L56) and
[actions/generic.py:94](oarepo_requests/actions/generic.py#L94).

Adding `"cancel": cls.cancel_action` routes cancellation through
`MakeTopicDraftMixin`. That mixin calls `read_draft(identity)` before
`OARepoGenericActionMixin.execute()` adds `request_active`, so `RequestActive()`
grants on `can_read_draft` do not apply to the conversion. Decline already
behaved this way.

For `publish_changed_metadata`, a missing or unreadable edit draft now makes
cancellation raise `ValueError`, which surfaces as HTTP 500. The previous plain
cancel action did not need the draft.

**Suggestion:** convert the topic inside the elevated scope, and let
cancellation succeed when the draft no longer exists.

**Validation:** cancel a `publish_changed_metadata` request after its edit draft
was discarded. Repeat with a workflow that grants `can_read_draft` only through
`RequestActive()`.

### B5. [P3] Remaining items

Still unchanged by the branch: finding 5 and the three smaller issues (tests
14--16). The walrus expression at
[types/publish_base.py:83](oarepo_requests/types/publish_base.py#L83) still
produces `Topic type True`. Finding 4 is fixed only in part: the guards are now
exhaustive, but they still consult only the search index.

Ruff reports these new unused imports:

- `opensearch_dsl`, which is also not a declared dependency, and
  `VersionAlreadyExists`, both in `utils.py`;
- `db` in `actions/delete_published_record.py`;
- `ConfiguratorMixin` in `resources/oarepo/config.py`;
- `ResolverRegistry` in `conditional.py`;
- `CancelAction` in `types/group_membership.py`.

## New findings

### N1. [P1, existing] An unresolvable topic breaks every read and listing that includes the request

Locations: [actions/generic.py:43](oarepo_requests/actions/generic.py#L43) and
[records/dumpers.py:27](oarepo_requests/records/dumpers.py#L27).

`OARepoGenericActionMixin.__init__` resolves the topic eagerly. Invenio's
request links call `_is_action_available()`, then `RequestActions.can_execute()`,
then `get_action()` for every available action of every serialized request,
whatever its status. Serializing a request therefore constructs every action,
and each construction resolves the topic.

When the topic no longer exists, `PIDDoesNotExistError` propagates:

- reading the request fails (404 at the API);
- every listing that contains the request fails, including the user requests
  dashboard, curator dashboards and record `?expand`;
- no action can be executed, not even cancel.

A temporary test reproduced this: create a `publish_draft` request, call
`delete_draft`, then `requests_service.read()`. The traceback runs through
`_is_action_available` into `actions/generic.py:43`.

The default workflow permissions make this easy to reach. A declined publish
request returns the draft to `draft`, where `can_delete_draft` lets the owner
discard it. The same happens with a created but unsubmitted request, and with a
discarded new-version draft. Nothing in the library closes open requests when a
draft is discarded.

`RecordReferenceDumperExt.dump()` also resolves the topic on every (re)index.
For example, commenting on such a request reindexes it and fails after the
database commit.

**Suggestion:**

- resolve the action topic lazily;
- let `can_execute()` and the dumper tolerate an unresolvable topic;
- add a `delete_draft` service component that cancels or deletes the draft's
  requests (compare RDM's `ReviewComponent.delete_draft`).

**Validation:** decline a publish request and discard the draft. Assert that the
request can be read, appears in the user's request search, and accepts a
comment. Separately, discard a draft that has a `created` request and verify
that the request is closed.

### N2. [P2, existing] Non-string payload fields are silently dropped on creation

Locations: [services/oarepo/service.py:109](oarepo_requests/services/oarepo/service.py#L109)
and [services/oarepo/service.py:133](oarepo_requests/services/oarepo/service.py#L133).

`OARepoRequestsService.create()` loads `data` with the request type's schema
and passes the *loaded* data to `RequestsService.create()`, which loads it again
with `raise_errors=False`. Fields whose deserialized value is not valid input
fail the second load and are left out of the stored payload, for example `Date`,
`DateTime`, and nested schemas with `post_load`.

The same double load in plain marshmallow produced
`{'payload': {'deadline': ['Not a valid date.']}}` and kept only the string
field. Built-in types use string payloads only, so custom request types are the
ones affected.

**Suggestion:** pass the original input to `super().create()`, and use the
loaded data only for receiver selection and `can_create()`.

**Validation:** define a test request type with a `Date` payload field, create a
request, and assert that the stored payload contains the date and the result
reports no errors.

### N3. [P2, existing] Expiration skips components and leaves the topic in its submitted state

Locations: [actions/components.py:180](oarepo_requests/actions/components.py#L180)
and [actions/components.py:235](oarepo_requests/actions/components.py#L235).

`expire` is still Invenio's `ExpireAction`, which does not include
`OARepoGenericActionMixin`, so no component runs: no workflow transition and no
notification. `WorkflowTransitions` has no `expired` key.
`WorkflowTransitionComponent.create()` and `.expire()` are unreachable; if they
ran, they would raise `KeyError` from `WorkflowTransitions.__getitem__`. The same
holds for `create`, which uses Invenio's `CreateAction`.

Finding 9 is now fixed, so `expires_at` is stored, and RDM schedules
`check_expired_requests`. An expired, submitted publish request therefore leaves
the draft in its submitted state (`publishing` in the test workflows) with no
open request. If requesters are gated on `IfInState("draft")`, the owner cannot
create a new request.

Separately, `created` is an open status for oarepo types, but `ExpireAction`
accepts only `submitted`. The periodic task therefore logs
`CannotExecuteActionError` on every run for expired `created` requests.

**Suggestion:**

- provide an oarepo expire action;
- support an expiry transition, either in oarepo-workflows or by mapping it to
  `cancelled`;
- remove or fix the dead hooks;
- define what expiry means for `created` requests.

**Validation:** submit a publish request with a past `expires_at`, run
`check_expired_requests`, and assert that the request is expired and the draft
is editable again.

### N4. [P2, existing] `payload.created_topic` is client-writable and can break expanded listings

Locations: [types/new_version.py:46](oarepo_requests/types/new_version.py#L46),
[services/results.py:38](oarepo_requests/services/results.py#L38) and
[utils.py:194](oarepo_requests/utils.py#L194).

`created_topic` is part of `NewVersionRequestType.payload_schema`, so a
requester can set it at creation. It is expanded through
`StringEntityResolverExpandableField`, which fails on bad values:

- `string_to_reference()` raises `IndexError` for a value without `:`;
- an unknown reference type makes `resolve_entity_proxy()` return `None`, which
  then raises `AttributeError`.

The expansion resolver catches neither, so any `expand=1` response that includes
the request returns 500. The user requests search always sends `expand=1`
([ext.py:206](oarepo_requests/ext.py#L206)). In a workflow where `new_version`
requires approval, a requester can break the receiver's dashboard until the
request is accepted; acceptance overwrites the value.

**Suggestion:** remove `created_topic` from the loadable payload, so that only
the action sets it. Also validate its format and make the expandable field skip
malformed values.

**Validation:** under an approval workflow, create a `new_version` request with
`{"created_topic": "garbage"}`. Either creation is rejected, or the receiver's
expanded search still succeeds.

### N5. [P3, existing] Notification recipient lookup and the comment builder

Locations: [notifications/generators/recipients.py:42](oarepo_requests/notifications/generators/recipients.py#L42)
and [notifications/builders/comment.py:43](oarepo_requests/notifications/builders/comment.py#L43).

- **No fallback for unknown entity types.** The default registry has generators
  only for `user`, `group` and `multiple`, and the lookup
  `current_notification_recipient_generators_registry[entity_type]` has no
  fallback.
  - An `auto_approve` receiver raises `KeyError`. `PublishDraftSubmitAction.apply`
    registers a submit notification unconditionally, so the notification for every
    auto-approved publish request fails in Celery.
  - `community` and `email` references fail the same way unless another package
    registers generators for them. This matters because the oarepo comment builder
    serves comments of all request types, including Invenio's own.
- **Topic resolution in comments.** The comment builder adds
  `ReferenceSavingEntityResolve("request.topic")`. Comments on an accepted
  `delete_published_record` request therefore fail with `RecordDeletedException`.
  That failure is exactly why the delete-accept builder
  ([builders/delete_published_record.py:32](oarepo_requests/notifications/builders/delete_published_record.py#L32))
  leaves the topic out.
- **Shared lists mutated in place.** `super().context` and `super().recipients`
  return Invenio's class-level lists, which this code then mutates in place. The
  change leaks into Invenio's `CommentRequestEventCreateNotificationBuilder` and
  into `CommentRequestEventReplyNotificationBuilder`, which shares the inherited
  `context` list.

**Suggestion:** skip (and log) entity types without a recipient generator, make
topic resolution in the comment context tolerant, and build new tuples instead
of mutating the inherited lists.

### N6. [P3, existing] Expected client errors return HTTP 500

None of the following exceptions has an error handler:

- `ValueError` and `TypeError` from `PublishRequestType.convert_topic()`
  ([types/publish_base.py:107](oarepo_requests/types/publish_base.py#L107),
  [:114](oarepo_requests/types/publish_base.py#L114)), and the topic-type mismatch
  ([:84](oarepo_requests/types/publish_base.py#L84));
- the draft checks in `EditPublishedRecordRequestType.can_create()` and
  `NewVersionRequestType.can_create()`
  ([types/edit_record.py:75](oarepo_requests/types/edit_record.py#L75),
  [types/new_version.py:71](oarepo_requests/types/new_version.py#L71));
- `raise ValueError("")` for a missing topic
  ([services/oarepo/service.py:97](oarepo_requests/services/oarepo/service.py#L97));
- malformed topic strings in `string_to_reference()`, which raise `IndexError`;
  this also affects `POST /requests/<topic>/<request_type>`;
- `GET /requests/applicable` without `topic`
  ([resources/oarepo/resource.py:112](oarepo_requests/resources/oarepo/resource.py#L112),
  `KeyError`), or with a group topic
  ([services/oarepo/service.py:151](oarepo_requests/services/oarepo/service.py#L151),
  `TypeError`), even though `group_membership` is a group-topic type;
- following the `self` link of `RequestTypesList`
  ([services/oarepo/service.py:158](oarepo_requests/services/oarepo/service.py#L158)),
  which omits `topic`.

**Suggestion:** raise or map these as 400-level or validation errors, validate
the topic argument, and include `topic` in the `self` link.

### N7. [P3, existing] `open_request_exists()` serializes a page of hits to test existence

Location: [utils.py:150](oarepo_requests/utils.py#L150).

`bool(list(search(...).hits))` loads and dumps up to a full page of requests,
including link rendering. That means constructing every action and resolving
the topic for each, plus `validate_draft()` for open publish requests through
`PublishMixin.can_execute()`. It runs for each non-duplicable type in
`is_applicable_to()` on every record expansion, and again in `can_create()`.
Reading `total` (or calling `count()` on the search) is enough.

Related: `_ensure_title`
([types/generic.py:138](oarepo_requests/types/generic.py#L138)) resolves the
topic for every dumped request, which costs one extra query per hit. B3 makes
the number of hits unbounded.

### N8. [P3, existing] Workflow configuration drift

- `allowed_request_types_for_record()` and `get_receiver_for_request_type()`
  ([utils.py:82](oarepo_requests/utils.py#L82), [:224](oarepo_requests/utils.py#L224))
  catch `MissingWorkflowError` but not `InvalidWorkflowError`. A record whose
  workflow code was removed from configuration therefore returns 500 on
  `?expand`. `WorkflowTransitionComponent` and `receiver.py` catch both.
- `WorkflowTransitionComponent`
  ([actions/components.py:165](oarepo_requests/actions/components.py#L165)) does
  not handle `RequestTypeNotInWorkflowError`. A request whose type is no longer
  in the record's workflow cannot be cancelled or declined.
- Without a workflow, `allowed_request_types_for_record()` returns every
  record-topic request type, with no `is_applicable_to()` or permission checks.
  That contradicts its docstring.

### N9. [P3, existing] Action keyword arguments cannot be forwarded

Locations: [actions/generic.py:97](oarepo_requests/actions/generic.py#L97) and
[actions/publish_draft.py:140](oarepo_requests/actions/publish_draft.py#L140).

`OARepoGenericActionMixin.execute()` passes `*args, **kwargs` to Invenio's
`RequestAction.execute(identity, uow)`, which accepts neither. Any extra keyword
passed to `execute_action()` raises `TypeError`, so `PublishDraftAcceptAction`
can never actually forward keyword arguments to `publish()`. This is related to
`execute-action-wrapper.patch`.

### N10. [P3, existing] Config initialisation

Locations: [ext.py:152](oarepo_requests/ext.py#L152), [:164](oarepo_requests/ext.py#L164)
and [config.py:34](oarepo_requests/config.py#L34).

`init_config()` calls `.extend()` on the user's `REQUESTS_ACTION_COMPONENTS` and
`REQUESTS_ALLOWED_RECEIVERS`.

- A tuple, which is the type of the library's own default, crashes app
  start-up.
- The defaults are always appended, so users can neither remove nor reorder
  them, despite the "let the user override" comment.
- Listing the defaults explicitly duplicates them.

### N11. [P3, existing] Version-label uniqueness covers only the payload path

Locations: `PublishDraftSubmitAction.apply()` and
`PublishNewVersionRequestType.can_create()`.

Uniqueness is checked only for `payload.version`, at creation and submission.
The following are never checked:

- setting `metadata.version` directly in a draft;
- publishing, through `publish_changed_metadata`, an edit of an older version
  that carries another version's label.

The label is also not rechecked at acceptance.

### N12. [P3, existing] `NewVersionAcceptAction` keeps the published record as the topic

Location: [actions/new_version.py:37](oarepo_requests/actions/new_version.py#L37).

`EditTopicAcceptAction` switches `self.topic` to the new draft, but the
new-version accept action leaves the published record as `self.topic`. An
`accepted` transition configured for `new_version` would therefore change the
published record's state. This is latent, because the test workflows define no
transitions for `new_version`.

### N13. [P3, existing] `PublishMixin.can_execute()` swallows all exceptions

Location: [actions/publish_draft.py:73](oarepo_requests/actions/publish_draft.py#L73).

The bare `except:` has three effects:

- draft validation failures at submit or accept become a generic "cannot
  execute" 400 without field errors;
- database errors are swallowed too, which may leave the session in a failed
  state;
- the full `validate_draft()` it runs is part of link rendering for every open
  publish request.

### N14. [P3] Smaller items

- `current_oarepo_requests_resource`
  ([proxies.py:30](oarepo_requests/proxies.py#L30)) reads `requests_resource`,
  which the state object does not have.
- `OARepoRequests.__getattr__` ([ext.py:144](oarepo_requests/ext.py#L144))
  returns `None` for any missing attribute, which hides typos.
- `merge_resource_configs()` and `reference_to_tuple()` in `utils.py` are
  unused.
- `OARepoGenericActionMixin.execute()` adds and removes `request_active` on the
  identity it is given. That includes the process-global `system_identity`,
  where it is pointless, since that identity already passes every check, and is
  not thread-safe. The grant is also not scoped to the request's topic.

## Answers to remaining REVIEW questions

- **`types/generic.py:234`, `string_by_state()`.** Only `stateful_name()` and
  `stateful_description()` call it. Those are used only by tests and by the
  title fallback in `RequestEntityResolve`. That fallback never runs, because
  `_ensure_title` always sets `title`. When `request.created_by` is an entity
  proxy, it also crashes in `request_identity_matches()`, as the comment in
  `_ensure_title` notes. It is a candidate for removal.
- **`utils.py:344`, `applicable_requests()`.** Only tests use it.
- **`services/results.py:85`.** `applicable_request_types()` never passes
  `links_item_tpl`, so this branch is dead.
- **`config.py:40`, `PUBLISH_REQUEST_TYPES`.** Nothing in the library or the
  installed dependencies reads it; only `init_config()` sets it.
- **`types/publish_base.py:116`.** Deletion neither checks nor closes other open
  requests on the record. On soft-deleted RDM records those requests stay
  actionable; on discarded drafts they turn into N1.

Suggested order for this pass: N1 and B1, then B2, N2--N4 and B3, then the P3
items.
