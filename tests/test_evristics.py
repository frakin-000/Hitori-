from moduls import evristics


def test_field_have_solution_true_and_false():
    field_ok = [
        [1, -1, 2],
        [3, 4, -1],
    ]
    field_bad = [
        [-1, -1, 2],
        [3, 4, -1],
    ]
    assert evristics.field_have_solution(field_ok) is True
    assert evristics.field_have_solution(field_bad) is False


def test_evristics_check_simple():
    # простое поле без длинных последовательностей, эвристика должна пропустить
    field = [
        [1, 2, 3],
        [2, 3, 4],
    ]
    assert evristics.evristics_check(field) is True


def test_check_all_no_solution_due_to_adjacent_blacks():
    field = [
        [-1, -1, 1],
        [2, 3, 4],
    ]
    assert evristics.check_all(field) == "no solution"


def test_check_all_returns_dual_field():
    field = [
        [1, 1, 2],
        [2, 3, 3],
    ]
    res = evristics.check_all(field)
    # функция должна вернуть не строку "no solution", а массив/список поля
    assert not isinstance(res, str)
    # размерность сохраняется
    assert len(res) == len(field)
    assert len(res[0]) == len(field[0])


def test_evristics_check_false_on_long_run_row():
    # ряд из четырёх подряд одинаковых значений в строке должен нарушать эвристику
    field = [
        [1, 1, 1, 1],
        [2, 3, 4, 5],
    ]
    assert evristics.evristics_check(field) is False


def test_triads_marks_non_middle_positions_black():
    # В строке три подряд одинаковых числа: индексы [0,1,2].
    # По коду triads индекс = средний (1), а остальные должны стать -1.
    field = [
        [1, 1, 1, 2],
        [2, 3, 4, 5],
    ]
    res = evristics.triads(field)
    # в первой строке должны быть чёрными все позиции кроме средней из триады
    assert list(res[0]) == [-1, 1, -1, 2]


def test_duals_marks_singular_positions_black():
    # Конфигурация для duals: ..11..1..1.
    # В ряду четыре единицы, внутри есть пара подряд, остальные должны стать -1.
    field = [
        [0, 1, 1, 0, 1, 0, 1, 0],
        [2, 3, 4, 5, 6, 7, 8, 9],
    ]
    res = evristics.duals(field)
    # ожидаем, что останутся только две соседние 1, остальные 1 превратятся в -1
    row = list(res[0])
    assert row.count(1) == 2
    # и они должны быть соседними
    ones_idx = [i for i, v in enumerate(row) if v == 1]
    assert ones_idx[1] == ones_idx[0] + 1


def test_evristics_check_false_on_long_run_column():
    # длинная последовательность по столбцу должна тоже нарушать эвристику
    field = [
        [1, 2],
        [1, 3],
        [1, 4],
        [1, 5],
    ]
    assert evristics.evristics_check(field) is False
