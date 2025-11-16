"""Модуль реализует решение головоломки"""
import copy
from moduls import dictionary


def paint_other(field, i_ind, j_ind):
    pos = field[i_ind][j_ind]
    for i in range(len(field)):
        if field[i][j_ind] == pos and i != i_ind:
            field[i][j_ind] = -1
    for j in range(len(field[0])):
        if field[i_ind][j] == pos and j != j_ind:
            field[i_ind][j] = -1
    return field


def processing(field):
    dictionary = dict.fromkeys([i + 1 for i in range(len(field))])
    for i in range(len(field)):
        pre_dict = dict.fromkeys(set(field[i]), list())
        for h in set(field[i]):
            pre_list = list()
            for j in range(len(field[0])):
                if h == field[i][j]:
                    pre_list.append(j)
            pre_dict[h] = pre_list
        dictionary[i + 1] = pre_dict
    return dictionary


def row_solver(field, line, copy_dict, result):
    for i in copy_dict[line]:
        for j in copy_dict[line][i]:
            copy_field = copy.deepcopy(field)
            copy_field = paint_other(copy_field, line - 1, j)
            if line != len(copy_field):
                row_solver(copy_field, line + 1, copy_dict, result)
            else:
                result.append(copy_field)
    return result


def check_result(result):
    """Фильтрует решения, оставляя только те, где нет повторяющихся чисел
    ни в строках, ни в столбцах (кроме -1).
    """
    new_result = []
    for k in range(len(result)):
        field = result[k]
        out = False

        # проверка по строкам
        row_dict = processing(field)
        for i in row_dict:
            for value in row_dict[i]:
                if value != -1 and len(row_dict[i][value]) > 1:
                    out = True
                    break
            if out:
                break

        if out:
            continue

        # проверка по столбцам
        col_dict = dictionary.processing_transpose(field)
        for i in col_dict:
            for value in col_dict[i]:
                if value != -1 and len(col_dict[i][value]) > 1:
                    out = True
                    break
            if out:
                break

        if not out:
            new_result.append(field)

    return new_result


def contiguity_check(result):
    """Отбрасывает решения, где есть соседние по стороне чёрные клетки (-1)."""
    answer = []
    for k in result:
        out = False
        for i in range(len(k)):
            for j in range(len(k[i])):
                if k[i][j] == -1:
                    # проверяем соседей по стороне, учитывая границы поля
                    if i > 0 and k[i - 1][j] == -1:
                        out = True
                        break
                    if i < len(k) - 1 and k[i + 1][j] == -1:
                        out = True
                        break
                    if j > 0 and k[i][j - 1] == -1:
                        out = True
                        break
                    if j < len(k[i]) - 1 and k[i][j + 1] == -1:
                        out = True
                        break
            if out:
                break
        if not out:
            answer.append(k)
    return answer


def white_connected(field):
    """Проверяет, что все белые клетки (!= -1) образуют одну связную область по стороне."""
    h = len(field)
    w = len(field[0]) if h > 0 else 0

    # найдём первую белую клетку
    start = None
    total_white = 0
    for i in range(h):
        for j in range(w):
            if field[i][j] != -1:
                total_white += 1
                if start is None:
                    start = (i, j)

    # если белых клеток нет, формально считаем поле связным
    if total_white == 0:
        return True

    # BFS/DFS по белым клеткам
    stack = [start]
    visited = set([start])
    while stack:
        x, y = stack.pop()
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < h and 0 <= ny < w and field[nx][ny] != -1:
                if (nx, ny) not in visited:
                    visited.add((nx, ny))
                    stack.append((nx, ny))

    return len(visited) == total_white


def _diagonal_ok(field):
    """Проверяет, что диагональные соседи (белые клетки) имеют разные значения."""
    h = len(field)
    w = len(field[0]) if h > 0 else 0
    for i in range(h):
        for j in range(w):
            if field[i][j] == -1:
                continue
            val = field[i][j]
            # вправо-вниз
            if i + 1 < h and j + 1 < w and field[i + 1][j + 1] == val:
                return False
            # вправо-вверх
            if i - 1 >= 0 and j + 1 < w and field[i - 1][j + 1] == val:
                return False
            # влево-вниз
            if i + 1 < h and j - 1 >= 0 and field[i + 1][j - 1] == val:
                return False
            # влево-вверх
            if i - 1 >= 0 and j - 1 >= 0 and field[i - 1][j - 1] == val:
                return False
    return True


def _is_valid_solution(field, strict_diagonal=False):
    """Проверяет, что поле удовлетворяет стандартным правилам Hitori.

    Если strict_diagonal=True, дополнительно требует выполнения диагонального правила.
    """
    # уникальность чисел в строках и столбцах
    if not check_result([field]):
        return False
    # нет соседних по стороне чёрных клеток
    if not contiguity_check([field]):
        return False
    # белые клетки связны
    if not white_connected(field):
        return False
    # дополнительное правило по диагоналям (по желанию)
    if strict_diagonal and not _diagonal_ok(field):
        return False
    return True


def _has_adjacent_black(field, x, y):
    """Проверяет, есть ли у клетки (x, y) чёрные соседи по стороне."""
    h = len(field)
    w = len(field[0]) if h > 0 else 0
    if x > 0 and field[x - 1][y] == -1:
        return True
    if x < h - 1 and field[x + 1][y] == -1:
        return True
    if y > 0 and field[x][y - 1] == -1:
        return True
    if y < w - 1 and field[x][y + 1] == -1:
        return True
    return False


def _collect_duplicate_positions(field):
    """Возвращает список позиций (i, j), которые участвуют в повторах по строкам или столбцам."""
    h = len(field)
    w = len(field[0]) if h > 0 else 0
    dup = set()

    # по строкам
    for i in range(h):
        counts = {}
        for j in range(w):
            val = field[i][j]
            if val == -1:
                continue
            counts.setdefault(val, []).append((i, j))
        for cells in counts.values():
            if len(cells) > 1:
                dup.update(cells)

    # по столбцам
    for j in range(w):
        counts = {}
        for i in range(h):
            val = field[i][j]
            if val == -1:
                continue
            counts.setdefault(val, []).append((i, j))
        for cells in counts.values():
            if len(cells) > 1:
                dup.update(cells)

    return sorted(dup)


def _backtrack(field, dup_positions, index, solutions, max_solutions=None, strict_diagonal=False):
    """Бэктрекинг по дублирующимся клеткам: для каждой решаем, красить ли её в чёрный."""
    if max_solutions is not None and len(solutions) >= max_solutions:
        return

    if index >= len(dup_positions):
        # все дублирующиеся клетки рассмотрены — проверяем полное решение
        if _is_valid_solution(field, strict_diagonal=strict_diagonal):
            solutions.append(copy.deepcopy(field))
        return

    i, j = dup_positions[index]

    # если клетка уже закрашена эвристиками, просто идём дальше
    if field[i][j] == -1:
        _backtrack(field, dup_positions, index + 1, solutions, max_solutions, strict_diagonal=strict_diagonal)
        return

    # Вариант 1: покрасить клетку в чёрный
    original_value = field[i][j]
    field[i][j] = -1
    if not _has_adjacent_black(field, i, j):
        _backtrack(field, dup_positions, index + 1, solutions, max_solutions, strict_diagonal=strict_diagonal)
    field[i][j] = original_value

    # Вариант 2: оставить клетку белой
    _backtrack(field, dup_positions, index + 1, solutions, max_solutions, strict_diagonal=strict_diagonal)


def solution(dual_field, max_solutions=None, strict_diagonal=False):
    """Ищет решения (все или первые N) для поля после эвристической обработки.

    :param dual_field: поле после эвристической обработки
    :param max_solutions: None — вернуть все решения; целое число N — вернуть не более N решений
    :param strict_diagonal: если True — требовать также выполнение диагонального правила
    :return: список решений (каждое — поле); может быть пустым, если решений нет
    """
    # приводим поле к спискам Python, чтобы удобнее изменять
    field = [list(row) for row in dual_field]
    dup_positions = _collect_duplicate_positions(field)
    solutions = []
    _backtrack(field, dup_positions, 0, solutions, max_solutions, strict_diagonal=strict_diagonal)
    return solutions
