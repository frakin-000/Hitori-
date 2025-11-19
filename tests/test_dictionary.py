from moduls import dictionary


def test_processing_creates_expected_structure():
    field = [
        [1, 1, 2],
        [2, 3, 3],
    ]
    d = dictionary.processing(field)
    # должно быть по одной записи на строку (ключи 1 и 2)
    assert set(d.keys()) == {1, 2}
    # в первой строке число 1 встречается дважды, число 2 один раз
    row1 = d[1]
    assert set(row1.keys()) == {1, 2}
    assert row1[1] == [0, 1]
    assert row1[2] == [2]


def test_processing_transpose():
    field = [
        [1, 1, 2],
        [2, 3, 3],
    ]
    dt = dictionary.processing_transpose(field)
    # теперь ключи соответствуют столбцам
    assert set(dt.keys()) == {1, 2, 3}
    # в первом столбце 1 и 2
    col1 = dt[1]
    assert set(col1.keys()) == {1, 2}
