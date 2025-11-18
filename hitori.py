import collections
import numpy as np
import argparse
import copy
import sys

if sys.version_info < (3, 7):
    print('Use python >= 3.7', file=sys.stderr)
    sys.exit(ERROR_PYTHON_VERSION)

try:
    from moduls import dictionary, solver, evristics
except Exception as e:
    print('Game modules not found: "{}"'.format(e), file=sys.stderr)
    # sys.exit(ERROR_MODULES_MISSING)


def read_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-fr", "--fileread", type=str, help="Reading from a file", default="none")
    parser.add_argument("-cr", "--consoleread", type=int, help="Reading from a console", default=0)
    parser.add_argument("-d", "--doc", type=str, help="Documentation", default="none")
    # Дополнительный параметр: сколько решений вывести (0 = все, по умолчанию 1)
    parser.add_argument("-n", "--solutions", type=int, help="Number of solutions to output (0 = all)", default=1)
    # Режим решения: обычный Hitori или с учётом диагональных соседей
    parser.add_argument("-m", "--mode", type=str, choices=["normal", "diagonal"],
                        help="Solve mode: normal Hitori or with diagonal neighbors constraint",
                        default="normal")
    cmd_args = parser.parse_args()
    return cmd_args


def input_from_the_file(filename):
    """Читает поле из файла и проверяет корректность формата.

    Требования:
    - все строки содержат одинаковое количество чисел;
    - все токены являются целыми числами.
    При нарушении условий выбрасывает IOError("Invalid input format").
    """
    with open(filename, 'r') as file:
        raw_lines = [line.strip() for line in file.readlines()]

    # убираем пустые строки по краям
    field_str = [line for line in raw_lines if line != ""]
    if not field_str:
        raise IOError("Invalid input format")

    field_tokens = [line.split() for line in field_str]
    n = len(field_tokens[0])
    if n == 0:
        raise IOError("Invalid input format")

    for row in field_tokens:
        if len(row) != n:
            raise IOError("Invalid input format")

    field = []
    try:
        for row in field_tokens:
            field.append([int(x) for x in row])
    except ValueError:
        raise IOError("Invalid input format")

    return field


def input_from_the_console(string_count):
    """Читает поле из консоли и проверяет корректность формата.

    Требования:
    - вводится ровно string_count строк;
    - во всех строках одинаковое количество чисел;
    - все токены являются целыми числами.
    При нарушении условий выбрасывает IOError("Invalid input format").
    """
    field = []

    # читаем первую строку и определяем ожидаемое количество столбцов
    first_line = input().split()
    if not first_line:
        raise IOError("Invalid input format")
    try:
        row = [int(x) for x in first_line]
    except ValueError:
        raise IOError("Invalid input format")

    n = len(row)
    field.append(row)

    # читаем оставшиеся строки
    for _ in range(string_count - 1):
        tokens = input().split()
        if len(tokens) != n:
            raise IOError("Invalid input format")
        try:
            row = [int(x) for x in tokens]
        except ValueError:
            raise IOError("Invalid input format")
        field.append(row)

    return field


def bound_field_check(field):
    """Проверка дополнительных ограничений на поле (оставлена для совместимости).

    Сейчас используется только диагональное правило.
    """
    return diagonal_rule_ok(field)


def diagonal_rule_ok(field):
    """Проверяет доп. правило: диагональные соседи (белые клетки) имеют разные значения."""
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


def _has_adjacent_black_local(field, x, y):
    """Локальная проверка: есть ли у клетки (x, y) чёрные соседи по стороне."""
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


def _collect_diagonal_conflicts(field):
    """Возвращает список позиций (i, j), которые образуют пары равных диагональных соседей."""
    h = len(field)
    w = len(field[0]) if h > 0 else 0
    conflicts = set()
    for i in range(h):
        for j in range(w):
            if field[i][j] == -1:
                continue
            val = field[i][j]
            for di, dj in ((1, 1), (-1, 1), (1, -1), (-1, -1)):
                ni, nj = i + di, j + dj
                if 0 <= ni < h and 0 <= nj < w and field[ni][nj] == val:
                    conflicts.add((i, j))
                    conflicts.add((ni, nj))
    return sorted(conflicts)


def fix_diagonal_solution(field):
    """Пытается добавить дополнительные чёрные клетки, чтобы убрать совпадения по диагоналям,
    сохраняя правила Hitori. Возвращает новое поле или None, если это невозможно.
    """
    from moduls import solver  # локальный импорт, чтобы избежать циклических зависимостей

    h = len(field)
    w = len(field[0]) if h > 0 else 0
    work = [row[:] for row in field]
    conflicts = _collect_diagonal_conflicts(work)
    if not conflicts:
        return work

    def backtrack(idx):
        if idx >= len(conflicts):
            # все конфликтующие клетки рассмотрены — проверяем финальное поле
            if diagonal_rule_ok(work) and solver.white_connected(work):
                return [row[:] for row in work]
            return None

        i, j = conflicts[idx]
        # если клетка уже чёрная, просто переходим дальше
        if work[i][j] == -1:
            return backtrack(idx + 1)

        original = work[i][j]

        # Вариант 1: покрасить клетку в чёрный, если не создаём чёрных соседей по стороне
        work[i][j] = -1
        result = None
        if not _has_adjacent_black_local(work, i, j):
            result = backtrack(idx + 1)
        work[i][j] = original
        if result is not None:
            return result

        # Вариант 2: оставить клетку белой
        return backtrack(idx + 1)

    return backtrack(0)


def main():
    flag = read_args()
    field = []
    try:
        if flag.fileread != 'none':
            field = input_from_the_file(flag.fileread)
        elif flag.consoleread != 0:
            field = input_from_the_console(flag.consoleread)
        elif flag.doc != "none":
            if flag.doc == "fileread":
                return ("name_program -fr(--fileread) name_file")
            elif flag.doc == "consoleread":
                return ("name_program -cr(--consoleread) count of row")
        else:
            raise IOError("Invalid mode")
    except IOError:
        # ошибка формата входных данных (разное число столбцов, нечисловые токены и т.п.)
        return "input error"

    dual_field = evristics.check_all(field)
    # если эвристики сразу говорят, что решения нет
    if isinstance(dual_field, str):
        return "no solution"

    # ищем решения; если flag.solutions == 0, то берём все, иначе не более заданного числа
    max_solutions = None if flag.solutions == 0 else flag.solutions

    # Обычный режим: решаем только по стандартным правилам Hitori
    if flag.mode == "normal":
        answers = solver.solution(dual_field, max_solutions=max_solutions, strict_diagonal=False)
        if not answers:
            return "no solution"
        if flag.solutions == 1:
            return answers[0]
        return answers

    # Диагональный режим.
    # 1) Сначала пытаемся найти решения, которые уже удовлетворяют диагональному правилу.
    diag_answers = solver.solution(dual_field, max_solutions=max_solutions, strict_diagonal=True)
    if diag_answers:
        if flag.solutions == 1:
            return diag_answers[0]
        return diag_answers

    # 2) Если строго диагональных решений нет, берём обычные решения и пробуем "починить" их,
    #    дорисовывая дополнительные чёрные клетки с помощью fix_diagonal_solution.
    base_answers = solver.solution(dual_field, max_solutions=None, strict_diagonal=False)
    if not base_answers:
        return "no solution"

    fixed = []
    for sol in base_answers:
        fixed_sol = fix_diagonal_solution(sol)
        if fixed_sol is not None:
            fixed.append(fixed_sol)
            if max_solutions is not None and len(fixed) >= max_solutions:
                break

    if not fixed:
        return "no solution"

    if flag.solutions == 1:
        return fixed[0]
    return fixed


if __name__ == '__main__':
    answer = main()
    if isinstance(answer, str):
        print(answer)
    else:
        def _print_field(field):
            # мягкая проверка диагонального правила: если нарушено, выводим предупреждение
            if not diagonal_rule_ok(field):
                print("Предупреждение: диагональные соседи могут совпадать")
            for i in range(len(field)):
                for j in range(len(field[i])):
                    if field[i][j] != -1:
                        print(' ', end='')
                    print(field[i][j], ' ', end="")
                print(end='\n')

        # answer может быть либо одним полем (list[list[int]]), либо списком решений (list[field])
        if answer and isinstance(answer, list) and isinstance(answer[0], list) and answer[0] and isinstance(answer[0][0], list):
            # список решений
            for idx, sol in enumerate(answer, 1):
                print(f"Solution {idx}:")
                _print_field(sol)
                if idx != len(answer):
                    print()
        else:
            # одно поле
            _print_field(answer)
