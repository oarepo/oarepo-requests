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
