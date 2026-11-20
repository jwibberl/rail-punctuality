import db


def test_get_connection_uses_supplied_credentials(monkeypatch):
    seen = {}
    expected = object()
    def fake_connect(**kwargs):
        seen.update(kwargs)
        return expected
    monkeypatch.setattr(db.psycopg2, 'connect', fake_connect)
    assert db.get_connection('localhost', 5432, 'tester', 'secret', 'rail') is expected
    assert seen == {'host': 'localhost', 'port': 5432, 'database': 'rail',
                    'user': 'tester', 'password': 'secret'}


def test_reset_db_truncates_and_commits(conn, cur):
    db.reset_db(conn)
    sql = cur.execute.call_args.args[0]
    for table in ('arrival', 'service_run', 'service', 'station'):
        assert table in sql
    assert 'RESTART IDENTITY CASCADE' in sql
    conn.commit.assert_called_once()


def test_reset_db_rolls_back_on_error(conn, cur, capsys):
    cur.execute.side_effect = RuntimeError('failed')
    db.reset_db(conn)
    conn.rollback.assert_called_once()
    conn.commit.assert_not_called()
    assert 'failed' in capsys.readouterr().out
