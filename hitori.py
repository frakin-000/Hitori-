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
    cmd_args = parser.parse_args()
    return cmd_args


def input_from_the_file(filename):
    with open(filename, 'r') as file:
        field_str = file.readlines()
    field = []
    for i in range(len(field_str) - 1):
        line = field_str[i][:-1]
        field.append(line.split())
    field.append(field_str[-1].split())
    n = len(field[0])
    for i in field:
        if len(i) != n:
            raise IOError("Invalid input format")
    for i in range(len(field)):
        for j in range(len(field[0])):
            field[i][j] = int(field[i][j])
    return field


def input_from_the_console(string_count):
    field = []
    line = list(map(int, input().split()))
    n = len(line)
    n1 = -1
    for i in range(string_count - 1):
        field.append(line)
        line = list(map(int, input().split()))
        n1 = len(line)
        if n1 != n:
            raise IOError("Invalid input format")
    field.append(line)
    return field


def bound_field_check(field):
    """Проверка дополнительных ограничений на поле.

    Оставлена для совместимости, сейчас просто вызывает diagonal_rule_ok.
    """
    return diagonal_rule_ok(field)


def diagonal_rule_ok(field):
    """Проверяет доп. правило: диагональные соседи (белые клетки) имеют разные значения."""
    for i in range(len(field)):
        for j in range(len(field[0])):
            if field[i][j] != -1:
                val = field[i][j]
                # вправо-вниз
                if i + 1 < len(field) and j + 1 < len(field[0]) and field[i + 1][j + 1] == val:
                    return False
                # вправо-вверх
                if i - 1 >= 0 and j + 1 < len(field[0]) and field[i - 1][j + 1] == val:
                    return False
                # влево-вниз
                if i + 1 < len(field) and j - 1 >= 0 and field[i + 1][j - 1] == val:
                    return False
                # влево-вверх
                if i - 1 >= 0 and j - 1 >= 0 and field[i - 1][j - 1] == val:
                    return False
    return True


def main():
    flag = read_args()
    field = []
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

    dual_field = evristics.check_all(field)
    # если эвристики сразу говорят, что решения нет
    if isinstance(dual_field, str):
        return "no solution"

    # ищем решения; если flag.solutions == 0, то берём все, иначе не более заданного числа
    max_solutions = None if flag.solutions == 0 else flag.solutions

    # Сначала пробуем найти решения, которые удовлетворяют также диагональному правилу
    diag_answers = solver.solution(dual_field, max_solutions=max_solutions, strict_diagonal=True)
    if diag_answers:
        # если пользователь не задал n (или n=1) — возвращаем одно решение
        if flag.solutions == 1:
            return diag_answers[0]
        # иначе возвращаем список решений (до n штук)
        return diag_answers

    # если диагональных решений нет — ищем обычные решения Hitori
    answers = solver.solution(dual_field, max_solutions=max_solutions, strict_diagonal=False)

    # нет ни одного стандартного решения Hitori
    if not answers:
        return "no solution"

    # если пользователь не задал n (или n=1) — возвращаем одно решение
    if flag.solutions == 1:
        return answers[0]

    # иначе возвращаем список решений (до n штук)
    return answers


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
