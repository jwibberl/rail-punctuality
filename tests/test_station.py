from unittest.mock import call
import station


def test_get_station_id_found(conn, cur):
    cur.fetchone.return_value = (42,)
    assert station.get_station_id(conn, 'LDS') == 42
    assert cur.execute.call_args.args[1] == ('LDS',)
    cur.close.assert_called_once()


def test_get_station_id_missing(conn, cur):
    cur.fetchone.return_value = None
    assert station.get_station_id(conn, 'XXX') is None


def test_add_station_commits(conn, cur):
    station.add_station(conn, 'LDS')
    assert cur.execute.call_args.args[1] == ('LDS',)
    conn.commit.assert_called_once()


def test_add_station_prints_error(conn, cur, capsys):
    cur.execute.side_effect = RuntimeError('insert failed')
    station.add_station(conn, 'LDS')
    assert 'insert failed' in capsys.readouterr().out
    conn.commit.assert_not_called()
    # Current implementation catches errors but does not roll back.


def test_add_stations_only_inserts_missing(conn, monkeypatch):
    lookups = {'LDS': None, 'KGX': 2, 'MAN': None}
    added = []
    monkeypatch.setattr(station, 'get_station_id', lambda c, name: lookups[name])
    monkeypatch.setattr(station, 'add_station', lambda c, name: added.append(name))
    data = {'Services': [
        {'serviceAttributesMetrics': {'origin_location': 'LDS', 'destination_location': 'KGX'}},
        {'serviceAttributesMetrics': {'origin_location': 'KGX', 'destination_location': 'MAN'}},
    ]}
    station.add_stations(conn, data)
    assert added == ['LDS', 'MAN']
