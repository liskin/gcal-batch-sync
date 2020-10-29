from __future__ import annotations

from contextlib import AbstractContextManager
import json
import os
from pathlib import Path
from typing import Any
from typing import Iterator
from typing import List
from typing import Optional

import appdirs  # type: ignore [import]
from google.auth.transport.requests import Request  # type: ignore [import]
from google.oauth2.credentials import Credentials  # type: ignore [import]
from google_auth_oauthlib.flow import InstalledAppFlow  # type: ignore [import]
from googleapiclient import discovery  # type: ignore [import]
from googleapiclient.errors import BatchError  # type: ignore [import]
from googleapiclient import http  # type: ignore [import]
from pkg_resources import resource_stream


def _load_token(filename: str) -> Credentials:
    try:
        return Credentials.from_authorized_user_file(filename)
    except Exception:
        return None


def _save_token(filename: str, token: Credentials) -> None:
    path = Path(filename)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(token.to_json())


def _obtain_token(filename: str, scopes: List[str]) -> Credentials:
    token = _load_token(filename)

    if not token or not token.valid:
        if token and token.expired and token.refresh_token:
            token.refresh(Request())
        else:
            with resource_stream(__package__, "client_secrets.json") as f:
                client_secrets = json.load(f)
            flow = InstalledAppFlow.from_client_config(client_secrets, scopes)
            token = flow.run_console()
        _save_token(filename, token)

    return token


def _list_paginate(resource: discovery.Resource, **kwargs) -> Iterator[Any]:
    if 'fields' in kwargs:
        kwargs['fields'] = f"nextPageToken,{kwargs['fields']}"

    req = resource.list(**kwargs)
    while req is not None:
        res = req.execute()
        for item in res['items']:
            yield item

        req = resource.list_next(req, res)


class BatchRequestError(Exception):
    def __init__(self, req, message):
        self.req = req
        self.message = message


class GCal:
    def __init__(self, token_filename: Optional[str] = None):
        if not token_filename:
            token_filename = os.path.join(appdirs.user_config_dir(appname=__package__), 'token.json')

        scopes = [
            "https://www.googleapis.com/auth/calendar.readonly",
            "https://www.googleapis.com/auth/calendar.events",
        ]

        self._api = discovery.build(
            "calendar", "v3",
            credentials=_obtain_token(filename=token_filename, scopes=scopes),
            cache_discovery=False,
        )

    def __call__(self) -> discovery.Resource:
        return self._api

    def list_calendars(self, **kwargs) -> Iterator[Any]:
        if 'maxResults' not in kwargs:
            kwargs['maxResults'] = 250
        return _list_paginate(self().calendarList(), **kwargs)

    def find_calendar(self, name: str, hidden: bool = False) -> Optional[Calendar]:
        for cal in self.list_calendars(fields="items(id,summary)", showHidden=hidden):
            if cal['summary'] == name:
                return self.calendar(cal['id'])
        return None

    def batch(self) -> Batch:
        return Batch(self)

    def calendar(self, id: str) -> Calendar:
        return Calendar(self, id)


class Batch(AbstractContextManager):
    def __init__(self, gcal: GCal):
        self._gcal = gcal
        self._batch_value = None

    def __call__(self) -> discovery.Resource:
        return self._gcal()

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        if not exc_value:
            self.flush()

    @property
    def _batch(self) -> http.BatchHttpRequest:
        if not self._batch_value:
            self._batch_value = self().new_batch_http_request()
        return self._batch_value

    def add(self, req: http.HttpRequest) -> None:
        def _batch_callback(request_id, response, exception) -> None:
            if exception:
                raise BatchRequestError(req.to_json(), f"request {request_id} failed") from exception

        try:
            self._batch.add(req, callback=_batch_callback)
        except BatchError:
            self.flush()
            self._batch.add(req)

    def flush(self) -> None:
        if self._batch:
            self._batch.execute()
            self._batch_value = None


class Calendar:
    def __init__(self, gcal: GCal, id: str):
        self._gcal = gcal
        self._id = id

    def __call__(self) -> discovery.Resource:
        return self._gcal()

    def list_events(self, **kwargs) -> Iterator[Any]:
        if 'maxResults' not in kwargs:
            kwargs['maxResults'] = 2500
        return _list_paginate(self().events(), calendarId=self._id, **kwargs)

    def insert_event_req(self, body) -> http.HttpRequest:
        return self().events().insert(
            calendarId=self._id,
            body=body,
            fields="kind",  # we don't need to get the event back
        )

    def import_event_req(self, body) -> http.HttpRequest:
        return self().events().import_(
            calendarId=self._id,
            body=body,
            fields="kind",  # we don't need to get the event back
        )

    def patch_event_req(self, eventId, body) -> http.HttpRequest:
        return self().events().patch(
            calendarId=self._id,
            eventId=eventId,
            body=body,
            fields="kind",  # we don't need to get the event back
        )

    def delete_event_req(self, eventId) -> http.HttpRequest:
        return self().events().delete(
            calendarId=self._id,
            eventId=eventId,
        )
