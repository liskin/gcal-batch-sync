import json
import os
from pathlib import Path
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


def calendar(token_filename: Optional[str] = None) -> discovery.Resource:
    if not token_filename:
        token_filename = os.path.join(appdirs.user_config_dir(appname=__package__), 'token.json')

    scopes = [
        "https://www.googleapis.com/auth/calendar.readonly",
        "https://www.googleapis.com/auth/calendar.events",
    ]

    return discovery.build(
        "calendar", "v3",
        credentials=_obtain_token(filename=token_filename, scopes=scopes),
        cache_discovery=False,
    )
