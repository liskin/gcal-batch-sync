from datetime import datetime
from datetime import timedelta
import os

import pytest  # type: ignore [import]
import pytz

from gcal_batch_sync.gcal import GCal


@pytest.mark.skipif(not os.getenv("PYTEST_ONLINE"), reason="PYTEST_ONLINE not enabled")
def test_gcal():
    cal = GCal()
    testcal = cal.find_calendar("gcal-sync-test", hidden=True)
    assert testcal

    time1 = datetime.fromtimestamp(1603972800, tz=pytz.utc)
    time2 = time1 + timedelta(hours=1)
    time3 = time2 + timedelta(hours=1)

    with cal.batch() as batch:
        batch.add(testcal.import_event_req({
            "summary": "test1",
            "iCalUID": "test1",
            "start": {"dateTime": time1.isoformat()},
            "end": {"dateTime": time2.isoformat()},
            "extendedProperties": {"shared": {"gcal-sync": "test"}},
        }))
        batch.add(testcal.import_event_req({
            "summary": "test2",
            "iCalUID": "test2",
            "start": {"dateTime": time2.isoformat()},
            "end": {"dateTime": time3.isoformat()},
            "extendedProperties": {"shared": {"gcal-sync": "test"}},
        }))

    events = {}
    for event in testcal.list_events(sharedExtendedProperty="gcal-sync=test", fields="items(id,iCalUID)"):
        events[event['iCalUID']] = event
    assert events['test1']
    assert events['test2']

    with cal.batch() as batch:
        batch.add(testcal.patch_event_req(events['test1']['id'], {
            "summary": "test1 patched",
        }))

    events_patched = {}
    for event in testcal.list_events(sharedExtendedProperty="gcal-sync=test", fields="items(iCalUID,summary)"):
        events_patched[event['iCalUID']] = event
    assert events_patched == {
        'test1': {'iCalUID': "test1", 'summary': "test1 patched"},
        'test2': {'iCalUID': "test2", 'summary': "test2"},
    }

    with cal.batch() as batch:
        batch.add(testcal.delete_event_req(events['test1']['id']))
        batch.add(testcal.delete_event_req(events['test2']['id']))

    assert list(testcal.list_events(sharedExtendedProperty="gcal-sync=test", fields="items(iCalUID)")) == []
