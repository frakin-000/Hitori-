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
    # сначала рассмотрим все клетки по отдельности на отделимость от других
    for i in range(1, len(field) - 1):
        for j in range(1, len(field[0]) - 1):
            if field[i][j] == -1:
                if i == 0 and j == 0:
                    if field[i + 1][j] == -1 and field[i][j + 1] == -1:
                        return False
                if i == 0 and j != 0 and j != len(field[0]) - 1:
                    if field[i + 1][j] == -1 and field[i][j + 1] == -1 and field[i][j - 1] == -1:
                        return False
                if i != 0 and j == 0 and i != len(field) - 1:
                    if field[i + 1][j] == -1 and field[i][j + 1] == -1 and field[i - 1][j] == -1:
                        return False
                if i == 0 and j == len(field[0]) - 1:
                    if field[i + 1][j] == -1 and field[i][j - 1] == -1:
                        return False
                if i == len(field) - 1 and j == 0:
                    if field[i - 1][j] == -1 and field[i][j + 1] == -1:
                        return False
                if i != 0 and i != len(field) - 1 and j == len(field[0]) - 1:
                    if field[i + 1][j] == -1 and field[i][j - 1] == -1 and field[i - 1][j] == -1:
                        return False
                if i == len(field) - 1 and j != 0 and j != len(field[0]) - 1:
                    if field[i][j + 1] == -1 and field[i][j - 1] == -1 and field[i - 1][j] == -1:
                        return False
                if i == len(field) - 1 and j == len(field[0]) - 1:
                    if field[i][j - 1] == -1 and field[i - 1][j] == -1:
                        return False
                else:
                    if field[i + 1][j] == -1 and field[i][j + 1] == -1 and field[i][j - 1] == -1 and field[i - 1][
                        j] == -1:
                        return False

    # теперь рассмотрим все диагонали
    # пойдем по правой стороне и будем проверять диагонали вправо вниз и вправо вверх
    i, j = 0, 0
    counter = 0
    while i != len(field) - 1:
        if field[i][j] == -1:
            i_i = i
            j_j = 0
            while i_i != len(field) or j_j != len(field[0]):
                if field[i_i][j_j] == -1:
                    i_i += 1
                    j_j += 1
                    counter += 1
                else:
                    break
            if counter == len(field) - i + 1:
                return False
            while i_i != -1 or j_j != len(field[0]):
                if field[i_i][j_j] == -1:
                    i_i -= 1
                    j_j += 1
                    counter += 1
                else:
                    break
            if counter == len(field) - i + 1:
                return False
        i += 1
    # теперь пойдем по левой стороне и будем проверять диагонали влево вниз и влево вверх
    i, j = 0, len(field[0]) - 1
    counter = 0
    while i != len(field) - 1:
        if field[i][j] == -1:
            i_i = i
            j_j = 0
            while i_i != len(field) or j_j != -1:
                if field[i_i][j_j] == -1:
                    i_i += 1
                    j_j -= 1
                    counter += 1
                else:
                    break
            if counter == len(field) - i + 1:
                return False
            counter = 0
            while i_i != -1 or j_j != -1:
                if field[i_i][j_j] == -1:
                    i_i -= 1
                    j_j -= 1
                    counter += 1
                else:
                    break
            if counter == i + 1:
                return False
            counter = 0
        i += 1
    # найти связные кружочки на поле (сделали для некоторых случаев)
    if len(field) == 6 and len(field[0]) == 6:
        for i in range(2):
            for j in range(2):
                cond1 = field[i][j + 2] == -1 and field[i + 2][j] == -1 and field[i + 4][j] == -1 and field[i + 2][
                    j + 4] == -1
                cond2 = field[i + 1][j + 1] == -1 and field[i + 1][j + 3] == -1 and field[i + 3][j + 1] == -1 and \
                        field[i + 3][j + 3] == -1
                if cond1 and cond2:
                    return False
    if len(field) == 7 and len(field[0]) == 7:
        for i in range(3):
            for j in range(3):
                cond1 = field[i][j + 2] == -1 and field[i + 2][j] == -1 and field[i + 4][j] == -1 and field[i + 2][
                    j + 4] == -1
                cond2 = field[i + 1][j + 1] == -1 and field[i + 1][j + 3] == -1 and field[i + 3][j + 1] == -1 and \
                        field[i + 3][j + 3] == -1
                if cond1 and cond2:
                    return False
            cond1 = field[0][3] == -1 and field[3][0] == -1 and field[6][3] == -1 and field[3][6] == -1
            cond2 = field[1][2] == -1 and field[1][4] == -1 and field[5][2] == -1 and field[5][4] == -1
            cond3 = field[2][1] == -1 and field[4][1] == -1 and field[2][5] == -1 and field[4][5] == -1
            if cond1 and cond2 and cond3:
                return False
    if len(field) == 8 and len(field[0]) == 8:
        for i in range(4):
            for j in range(4):
                cond1 = field[i][j + 2] == -1 and field[i + 2][j] == -1 and field[i + 4][j] == -1 and field[i + 2][
                    j + 4] == -1
                cond2 = field[i + 1][j + 1] == -1 and field[i + 1][j + 3] == -1 and field[i + 3][j + 1] == -1 and \
                        field[i + 3][j + 3] == -1
                if cond1 and cond2:
                    return False
        for i in range(2):
            for j in range(2):
                cond1 = field[i][j + 3] == -1 and field[i + 3][j] == -1 and field[i + 6][j + 3] == -1 and field[i + 3][
                    j + 6] == -1
                cond2 = field[i + 1][j + 2] == -1 and field[i + 1][j + 4] == -1 and field[i + 5][j + 2] == -1 and \
                        field[i + 5][j + 4] == -1
                cond3 = field[i + 2][j + 1] == -1 and field[i + 4][j + 1] == -1 and field[i + 2][j + 5] == -1 and \
                        field[i + 4][j + 5] == -1
                if cond1 and cond2 and cond3:
                    return False
    if len(field) == 9 and len(field[0]) == 9:
        for i in range(5):
            for j in range(5):
                cond1 = field[i][j + 2] == -1 and field[i + 2][j] == -1 and field[i + 4][j] == -1 and field[i + 2][
                    j + 4] == -1
                cond2 = field[i + 1][j + 1] == -1 and field[i + 1][j + 3] == -1 and field[i + 3][j + 1] == -1 and \
                        field[i + 3][j + 3] == -1
                if cond1 and cond2:
                    return False
        for i in range(3):
            for j in range(3):
                cond1 = field[i][j + 3] == -1 and field[i + 3][j] == -1 and field[i + 6][j + 3] == -1 and field[i + 3][
                    j + 6] == -1
                cond2 = field[i + 1][j + 2] == -1 and field[i + 1][j + 4] == -1 and field[i + 5][j + 2] == -1 and \
                        field[i + 5][j + 4] == -1
                cond3 = field[i + 2][j + 1] == -1 and field[i + 4][j + 1] == -1 and field[i + 2][j + 5] == -1 and \
                        field[i + 4][j + 5] == -1
                if cond1 and cond2 and cond3:
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
    answer = solver.solution(dual_field)
    if not bound_field_check(answer):
        return "no solution"
    return answer


if __name__ == '__main__':
    answer = main()
    if type(answer) == str:
        print(answer)
    else:
        for i in range(len(answer)):
            for j in range(len(answer[i])):
                if answer[i][j] != -1:
                    print(' ', end='')
                print(answer[i][j], ' ', end="")
            print(end='\n')
