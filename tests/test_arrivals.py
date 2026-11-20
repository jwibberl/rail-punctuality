from datetime import datetime
from unittest.mock import Mock
import pytest
import arrivals


def sample_data(rid='202611200001'):
    return {'Services': [{'serviceAttributesMetrics': {'rids': [rid]}}]}


def sample_details(locations):
    return {'serviceAttributesDetails': {'locations': locations}}


def location(station='LDS', scheduled='1000', actual='1003'):
    return {'location': station, 'gbtt_pta': scheduled, 'gbtt_ptd': None,
            'actual_ta': actual, 'actual_td': None}


def test_add_arrival_commits(conn, cur):
    arrivals.add_arrival(conn, 1, 2, 'scheduled', 'actual', 3)
    assert cur.execute.call_args.args[1] == (1, 2, 'scheduled', 'actual', 3)
    conn.commit.assert_called_once()


def test_add_arrival_rolls_back_on_error(conn, cur, capsys):
    cur.execute.side_effect = RuntimeError('insert failed')
    arrivals.add_arrival(conn, 1, 2, 'scheduled', 'actual', 3)
    conn.rollback.assert_called_once()
    assert 'insert failed' in capsys.readouterr().out


def test_get_service_details_posts_rid_and_api_key(monkeypatch):
    post = Mock(return_value=Mock(**{'json.return_value': {'ok': True}}))
    monkeypatch.setattr(arrivals.requests, 'post', post)
    assert arrivals.get_service_details('202611200001', 'test-key') == {'ok': True}
    args, kwargs = post.call_args
    assert args[0].endswith('/serviceDetails')
    assert kwargs['headers']['x-apikey'] == 'test-key'
    assert kwargs['json'] == {'rid': '202611200001'}


def test_add_arrivals_calculates_delay(conn, cur, monkeypatch):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([location()]))
    cur.fetchone.side_effect = [(10,), (20,)]  # run_id, station_id
    captured = []
    monkeypatch.setattr(arrivals, 'add_arrival', lambda *args: captured.append(args))
    arrivals.add_arrivals(conn, sample_data(), 'test-key')
    assert captured == [(conn, 10, 20, datetime(2026, 11, 20, 10),
                         datetime(2026, 11, 20, 10, 3), 3.0)]


def test_add_arrivals_uses_departure_times_as_fallback(conn, cur, monkeypatch):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    loc = {'location': 'LDS', 'gbtt_pta': None, 'gbtt_ptd': '1010',
           'actual_ta': None, 'actual_td': '1012'}
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([loc]))
    cur.fetchone.side_effect = [(10,), (20,)]
    captured = []
    monkeypatch.setattr(arrivals, 'add_arrival', lambda *args: captured.append(args))
    arrivals.add_arrivals(conn, sample_data(), 'test-key')
    assert captured[0][-1] == 2.0


def test_add_arrivals_skips_missing_run(conn, cur, monkeypatch, capsys):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([location()]))
    cur.fetchone.return_value = None
    insert = Mock()
    monkeypatch.setattr(arrivals, 'add_arrival', insert)
    arrivals.add_arrivals(conn, sample_data(), 'test-key')
    insert.assert_not_called()
    assert 'No service run found' in capsys.readouterr().out


def test_add_arrivals_skips_missing_station(conn, cur, monkeypatch, capsys):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([location()]))
    cur.fetchone.side_effect = [(10,), None]
    insert = Mock()
    monkeypatch.setattr(arrivals, 'add_arrival', insert)
    arrivals.add_arrivals(conn, sample_data(), 'test-key')
    insert.assert_not_called()
    assert 'Station not found' in capsys.readouterr().out


def test_add_arrivals_skips_missing_times(conn, cur, monkeypatch):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([location(actual=None)]))
    cur.fetchone.return_value = (10,)
    insert = Mock()
    monkeypatch.setattr(arrivals, 'add_arrival', insert)
    arrivals.add_arrivals(conn, sample_data(), 'test-key')
    insert.assert_not_called()
    assert cur.execute.call_count == 1


def test_add_arrivals_rolls_back_and_raises_on_invalid_data(conn, cur, monkeypatch):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: {'invalid': True})
    with pytest.raises(KeyError):
        arrivals.add_arrivals(conn, sample_data(), 'test-key')
    conn.rollback.assert_called_once()


@pytest.mark.xfail(reason='Current code uses datetime.replace(day=day+1), which fails at month end', strict=True)
def test_add_arrivals_crosses_month_boundary(conn, cur, monkeypatch):
    monkeypatch.setattr(arrivals.time, 'sleep', lambda seconds: None)
    monkeypatch.setattr(arrivals, 'get_service_details', lambda rid, key: sample_details([location(scheduled='2358', actual='0003')]))
    cur.fetchone.side_effect = [(10,), (20,)]
    captured = []
    monkeypatch.setattr(arrivals, 'add_arrival', lambda *args: captured.append(args))
    arrivals.add_arrivals(conn, sample_data('202611300001'), 'test-key')
    assert captured[0][-1] == 5.0
