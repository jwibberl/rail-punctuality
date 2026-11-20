import pytest
import graph


def test_render_graph_prints_counts_for_each_station(conn, cur, capsys):
    cur.fetchall.return_value = [(1, 'Leeds'), (2, 'York')]
    cur.fetchone.side_effect = [(3, 5, 8), (1, 2, 4)]
    graph.render_graph(conn)
    output = capsys.readouterr().out
    assert 'Leeds: <1 min = 3, <2 min = 5, <5 min = 8' in output
    assert 'York: <1 min = 1, <2 min = 2, <5 min = 4' in output
    assert [c.args[1] for c in cur.execute.call_args_list[1:]] == [(1,), (2,)]


def test_render_graph_empty_stations(conn, cur, capsys):
    cur.fetchall.return_value = []
    graph.render_graph(conn)
    assert capsys.readouterr().out == ''
    assert cur.execute.call_count == 1


def test_render_graph_propagates_errors(conn, cur, capsys):
    cur.execute.side_effect = RuntimeError('query failed')
    with pytest.raises(RuntimeError, match='query failed'):
        graph.render_graph(conn)
    assert 'error rendering graph' in capsys.readouterr().out
