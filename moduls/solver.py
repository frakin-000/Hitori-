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
    new_result = []
    count = 0
    for k in range(len(result)):
        new_dict = processing(result[k])
        out = False
        for i in new_dict:
            for j in new_dict[i]:
                if j != -1 and len(new_dict[i][j]) > 1:
                    out = True
                    break
            if out: break
        if not out:
            new_result.append(result[k])
    return new_result


def contiguity_check(result):
    answer = []
    count = 0
    for k in result:
        out = False
        for i in range(len(k) - 1):
            for j in range(len(k[i]) - 1):
                if i != len(k[i]) - 2:
                    if k[i][j] == -1 and (k[i][j + 1] == -1 or k[i + 1][j] == -1):
                        out = True
                        break
                else:
                    if k[i][j] == -1 and k[i][j + 1] == -1:
                        out = True
                        break
            if out: break
        if not out:
            answer.append(k)
    return answer


def solution(dual_field):
    result = []
    pre_result = row_solver(dual_field, 1, dictionary.processing(dual_field), result)
    check_answer = check_result(pre_result)
    answer = contiguity_check(check_answer)[0]
    return answer
