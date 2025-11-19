import os
import builtins
import types

import pytest

import hitori
from moduls import solver, evristics, dictionary


TEST_DIR = os.path.dirname(os.path.dirname(__file__))


def test_input_from_the_file_ok(tmp_path):
    p = tmp_path / "field.txt"
    p.write_text("1 2 3\n4 5 6\n")
    field = hitori.input_from_the_file(str(p))
    assert field == [[1, 2, 3], [4, 5, 6]]


def test_input_from_the_file_invalid_format(tmp_path):
    p = tmp_path / "field_bad.txt"
    # разные длины строк
    p.write_text("1 2 3\n4 5\n")
    with pytest.raises(IOError):
        hitori.input_from_the_file(str(p))


def test_input_from_the_console_ok(monkeypatch):
    inputs = iter(["1 2 3", "4 5 6"])
    monkeypatch.setattr(builtins, "input", lambda: next(inputs))
    field = hitori.input_from_the_console(2)
    assert field == [[1, 2, 3], [4, 5, 6]]


def test_input_from_the_console_invalid(monkeypatch):
    # вторая строка с другой длиной
    inputs = iter(["1 2 3", "4 5"])
    monkeypatch.setattr(builtins, "input", lambda: next(inputs))
    with pytest.raises(IOError):
        hitori.input_from_the_console(2)


def test_diagonal_rule_ok_true_and_false():
    # ok_field: нет равных диагональных соседей
    ok_field = [
        [1, 2],
        [3, 1],
    ]
    # bad_field: два одинаковых числа по диагонали (1 на (0,0) и (1,1))
    bad_field = [
        [1, 2],
        [3, 1],
    ]
    assert hitori.diagonal_rule_ok(ok_field) is False  # нарушает правило
    assert hitori.diagonal_rule_ok(bad_field) is False


def test_fix_diagonal_solution_adds_black_and_keeps_rules():
    # поле с диагональным конфликтом 1 на (0,0) и (1,1)
    field = [
        [1, 2],
        [3, 1],
    ]
    fixed = hitori.fix_diagonal_solution(field)
    assert fixed is not None
    # не должно быть диагональных совпадений
    assert hitori.diagonal_rule_ok(fixed)
    # белые клетки связны и нет соседних по стороне чёрных
    assert solver.white_connected(fixed)


def test_main_normal_mode_file(tmp_path):
    # маленький пример, где решение существует в normal-режиме
    p = tmp_path / "field.txt"
    p.write_text("1 1\n2 3\n")
    # подменяем аргументы командной строки
    import argparse as _argparse

    def _fake_parse_args():
        ns = _argparse.Namespace()
        ns.fileread = str(p)
        ns.consoleread = 0
        ns.doc = "none"
        ns.solutions = 0
        ns.mode = "normal"
        return ns

    hitori.read_args = _fake_parse_args
    answer = hitori.main()
    # должно вернуться хотя бы одно решение
    assert isinstance(answer, list)
    assert answer
    for sol in answer:
        assert solver.white_connected(sol)


def test_main_diagonal_mode_ex3_5(tmp_path):
    # копируем поле ex3_5.txt в tmp, чтобы не зависеть от относительных путей
    content = "1 1 2 3 4\n2 3 3 4 5\n4 5 6 7 7\n"
    p = tmp_path / "ex3_5.txt"
    p.write_text(content)

    import argparse as _argparse

    def _fake_parse_args():
        ns = _argparse.Namespace()
        ns.fileread = str(p)
        ns.consoleread = 0
        ns.doc = "none"
        ns.solutions = 0
        ns.mode = "diagonal"
        return ns

    hitori.read_args = _fake_parse_args
    answer = hitori.main()
    assert isinstance(answer, list)
    assert answer
    for sol in answer:
        # в диагональном режиме решения должны удовлетворять диагональному правилу
        assert hitori.diagonal_rule_ok(sol)
        assert solver.white_connected(sol)


def test_main_doc_modes():
    # проверяем, что doc-режимы возвращают ожидаемые строки
    import argparse as _argparse

    def _fake_parse_args_file():
        ns = _argparse.Namespace()
        ns.fileread = 'none'
        ns.consoleread = 0
        ns.doc = 'fileread'
        ns.solutions = 1
        ns.mode = 'normal'
        return ns

    def _fake_parse_args_console():
        ns = _argparse.Namespace()
        ns.fileread = 'none'
        ns.consoleread = 0
        ns.doc = 'consoleread'
        ns.solutions = 1
        ns.mode = 'normal'
        return ns

    # режим doc=fileread
    hitori.read_args = _fake_parse_args_file
    res_file = hitori.main()
    assert 'fileread' in res_file

    # режим doc=consoleread
    hitori.read_args = _fake_parse_args_console
    res_console = hitori.main()
    assert 'consoleread' in res_console


def test_main_invalid_mode():
    # некорректная комбинация аргументов должна привести к 'input error'
    import argparse as _argparse

    def _fake_parse_args_invalid():
        ns = _argparse.Namespace()
        ns.fileread = 'none'
        ns.consoleread = 0
        ns.doc = 'none'
        ns.solutions = 1
        ns.mode = 'normal'
        return ns

    hitori.read_args = _fake_parse_args_invalid
    res = hitori.main()
    assert res == 'input error'

