import logging
from pprint import pprint

import click

from .gcal import GCal

logger = logging.getLogger(__name__)


@click.command(context_settings={'max_content_width': 120})
@click.option(
    '-v', '--verbose', count=True, expose_value=False,
    callback=lambda _ctx, _param, value: logging.basicConfig(
        level=(
            logging.DEBUG if value >= 2 else
            logging.INFO if value >= 1 else
            logging.WARNING),
        format="%(levelname)s - %(message)s",
    ),
    help="Logging verbosity (0 = WARNING, 1 = INFO, 2 = DEBUG)",
)
def cli() -> None:
    """
    TODO
    """
    cal = GCal()
    pprint(list(cal.list_calendars(fields="items(id,summary)")))
