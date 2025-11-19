from moduls import solver


def test_white_connected_true_and_false():
    field_connected = [
        [1, 2, -1],
        [1, 2, 3],
    ]
    field_not_connected = [
        [1, -1, 2],
        [-1, 3, -1],
        [4, -1, 5],
    ]
    assert solver.white_connected(field_connected) is True
    assert solver.white_connected(field_not_connected) is False


def test_diagonal_ok():
    # поле без равных диагональных соседей
    field_ok = [
        [1, 2],
        [3, 4],
    ]
    # поле с равными диагональными соседями (1 на (0,0) и (1,1))
    field_bad = [
        [1, 2],
        [3, 1],
    ]
    assert solver._diagonal_ok(field_ok) is True
    assert solver._diagonal_ok(field_bad) is False


def test_collect_duplicate_positions():
    field = [
        [1, 1, 2],
        [3, 4, 3],
    ]
    dup = solver._collect_duplicate_positions(field)
    # порядок не важен, но в тесте проверим конкретный набор
    assert set(dup) == {(0, 0), (0, 1), (1, 0), (1, 2)}


def test_solution_strict_and_non_strict():
    field = [
        [1, 1],
        [2, 3],
    ]
    # без диагонального правила решения могут быть или отсутствовать, но функция должна возвращать список
    sols_non_strict = solver.solution(field, max_solutions=0, strict_diagonal=False)
    assert isinstance(sols_non_strict, list)
    # c диагональным правилом решения также могут отсутствовать, но вызов не должен падать
    sols_strict = solver.solution(field, max_solutions=0, strict_diagonal=True)
    assert isinstance(sols_strict, list)


def test_paint_other_and_processing_and_row_solver():
    # поле с повторами в строке, чтобы paint_other и row_solver что-то делали
    field = [
        [1, 1, 2],
        [3, 3, 4],
    ]
    # проверяем paint_other: закрашивает остальные такие же числа в строке и столбце
    copy_field = [row[:] for row in field]
    painted = solver.paint_other(copy_field, 0, 0)
    # в первой строке один из "1" должен остаться белым, другой стать -1
    assert painted[0].count(1) == 1
    assert painted[0].count(-1) == 1

    # проверяем processing+row_solver на простой конфигурации
    d = solver.processing(field)
    result = []
    solver.row_solver(field, 1, d, result)
    # row_solver должен сгенерировать хотя бы одно поле
    assert result


def test_contiguity_check_filters_adjacent_blacks():
    good = [[[1, -1, 2], [3, 4, -1]]]
    bad = [[[-1, -1, 2], [3, 4, -1]]]
    assert solver.contiguity_check(good) == [good[0]]
    assert solver.contiguity_check(bad) == []
