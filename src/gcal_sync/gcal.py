from __future__ import annotations

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

    def find_calendar(self, name: str) -> Optional[Calendar]:
        for cal in self.list_calendars(fields="items(id,summary)"):
            if cal['summary'] == name:
                return Calendar(self, cal['id'])
        return None


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
