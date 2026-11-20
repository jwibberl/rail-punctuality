from datetime import date
from unittest.mock import call
import pytest
import service


def test_get_service_found(conn, cur):
    cur.fetchone.return_value = (7,)
    assert service.get_service(conn, 1, 2) == 7
    assert cur.execute.call_args.args[1] == (1, 2)


def test_get_service_missing(conn, cur):
    cur.fetchone.return_value = None
    assert service.get_service(conn, 1, 2) is None


def test_add_service_returns_id_and_commits(conn, cur):
    cur.fetchone.return_value = (9,)
    assert service.add_service(conn, 1, 2) == 9
    assert cur.execute.call_args.args[1] == (1, 2)
    conn.commit.assert_called_once()


def test_add_service_rolls_back_on_error(conn, cur):
    cur.execute.side_effect = RuntimeError('db error')
    assert service.add_service(conn, 1, 2) is None
    conn.rollback.assert_called_once()


def test_add_service_run_returns_id(conn, cur):
    cur.fetchone.return_value = (19,)
    assert service.add_service_run(conn, 9, '202611200001', date(2026, 11, 20)) == 19
    assert cur.execute.call_args.args[1] == (9, '202611200001', date(2026, 11, 20))
    conn.commit.assert_called_once()


def test_add_service_run_rolls_back_on_error(conn, cur):
    cur.execute.side_effect = RuntimeError('db error')
    assert service.add_service_run(conn, 9, 'rid', date(2026, 11, 20)) is None
    conn.rollback.assert_called_once()


def test_add_services_inserts_routes(conn, cur, monkeypatch):
    monkeypatch.setattr(service.station, 'get_station_id', lambda c, code: {'LDS': 1, 'KGX': 2}[code])
    data = {'Services': [{'serviceAttributesMetrics': {'origin_location': 'LDS', 'destination_location': 'KGX'}}]}
    service.add_services(conn, data)
    assert cur.execute.call_args.args[1] == (1, 2)
    conn.commit.assert_called_once()


def test_add_services_rolls_back_and_raises(conn, cur, monkeypatch):
    monkeypatch.setattr(service.station, 'get_station_id', lambda c, code: 1)
    cur.execute.side_effect = RuntimeError('duplicate')
    data = {'Services': [{'serviceAttributesMetrics': {'origin_location': 'LDS', 'destination_location': 'KGX'}}]}
    with pytest.raises(RuntimeError, match='duplicate'):
        service.add_services(conn, data)
    conn.rollback.assert_called_once()


def test_add_service_runs_parses_rid_date(conn, cur, monkeypatch):
    monkeypatch.setattr(service.station, 'get_station_id', lambda c, code: {'LDS': 1, 'KGX': 2}[code])
    cur.fetchone.return_value = (8,)
    data = {'Services': [{'serviceAttributesMetrics': {
        'origin_location': 'LDS', 'destination_location': 'KGX',
        'rids': ['202611200001', '202611210002']}}]}
    service.add_service_runs(conn, data)
    args = [c.args[1] for c in cur.execute.call_args_list]
    assert args == [(1, 2), (8, '202611200001', date(2026, 11, 20)),
                    (8, '202611210002', date(2026, 11, 21))]
    conn.commit.assert_called_once()


def test_add_service_runs_skips_missing_route(conn, cur, monkeypatch):
    monkeypatch.setattr(service.station, 'get_station_id', lambda c, code: 1)
    cur.fetchone.return_value = None
    data = {'Services': [{'serviceAttributesMetrics': {
        'origin_location': 'LDS', 'destination_location': 'KGX', 'rids': ['202611200001']}}]}
    service.add_service_runs(conn, data)
    assert cur.execute.call_count == 1
    conn.commit.assert_called_once()


def test_add_service_runs_invalid_rid_rolls_back(conn, cur, monkeypatch):
    monkeypatch.setattr(service.station, 'get_station_id', lambda c, code: 1)
    cur.fetchone.return_value = (8,)
    data = {'Services': [{'serviceAttributesMetrics': {
        'origin_location': 'LDS', 'destination_location': 'KGX', 'rids': ['bad']}}]}
    with pytest.raises(ValueError):
        service.add_service_runs(conn, data)
    conn.rollback.assert_called_once()
