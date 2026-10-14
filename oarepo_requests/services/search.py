# SPDX-FileCopyrightText: 2025 CESNET z.s.p.o
# SPDX-License-Identifier: MIT

"""OARepo requests search."""

from __future__ import annotations

from invenio_requests.resources.requests.config import RequestSearchRequestArgsSchema
from invenio_requests.services.requests.config import RequestSearchOptions
from marshmallow import fields

from oarepo_requests.services.facets.params import (
    IsClosedParam,
    RequestAllAvailableFilterParam,
    RequestNotOwnerFilterParam,
    RequestOwnerFilterParam,
)

# TODO: idk how to type partials
# claude suggestion
"""
    ● Type them by what invenio does with them, not as partial. The search service only calls each entry with
    the search options class:

      # invenio_records_resources/services/records/service.py:188
      for interpreter_cls in search_opts.params_interpreters_cls:
          interpreter_cls(search_opts).apply(...)

      So each entry is a factory: a callable that takes the search options class and returns a ParamInterpreter.
       A class works, and so does a partial with the leading arguments already filled in:

      type ParamInterpreterFactory = Callable[[type[SearchOptions]], ParamInterpreter]

      1. Make the factories return that callable (services/facets/params.py):

      @classmethod
      def factory(cls, param: str) -> Callable[[type[SearchOptions]], Self]:
          return partial(cls, param)

      Callers don't need to know the factory uses partial. ty checks the partial(cls, param) against
      the declared return type and accepts it.

      2. Widen the stub type. ty's error is:

      tuple[*tuple[type[ParamInterpreter], ...], Any, Any, partial[ParamInterpreter], partial[Unknown]]
        is not assignable to tuple[type[ParamInterpreter], ...]

      The stub in invenio_records_resources-stubs/services/records/config.pyi:48 only allows classes,
      but invenio itself puts partials in this attribute (FilterParam.factory returns one). In
      oarepo-invenio-typing-stubs it should be:

      params_interpreters_cls: tuple[Callable[[type[SearchOptions]], ParamInterpreter], ...]

      A plain class like QueryStrParam still fits this type, because its constructor takes config.
      I checked a tuple mixing QueryStrParam, a typed .factory(...) result and a bare partial(P, "x") against this
      annotation with ty, and
      it passed.

      The two Any entries come from the stubs as well: FilterParam.factory returns Incomplete.
       They should become -> Callable[[type[SearchOptions]], Self] in the stubs too.

"""


class EnhancedRequestSearchOptions(RequestSearchOptions):
    """Searched options enhanced with additional filters."""

    params_interpreters_cls = (
        *RequestSearchOptions.params_interpreters_cls,
        RequestOwnerFilterParam.factory("mine", "created_by.user"),
        RequestNotOwnerFilterParam.factory("assigned", "created_by.user"),
        RequestAllAvailableFilterParam.factory("all"),
        IsClosedParam.factory("is_closed"),
    )


class ExtendedRequestSearchRequestArgsSchema(RequestSearchRequestArgsSchema):
    """Marshmallow schema for the extra filters."""

    mine = fields.Boolean()
    assigned = fields.Boolean()
    all = fields.Boolean()
    is_closed = fields.Boolean()
