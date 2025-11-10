"""Модуль реализует проверку эвристик"""
from moduls import dictionary
import numpy as np


def evristics_check(field):
    row_dict = dictionary.processing(field)
    column_dict = dictionary.processing_transpose(field)
    for i in row_dict:
        for j in row_dict[i]:
            if len(row_dict[i][j]) > 3:
                temp = 0
                count = 1
                for k in range(len(row_dict[i][j]) - 1):
                    if row_dict[i][j][k] + 1 == row_dict[i][j][k + 1]:
                        count += 1
                        if count > 3:
                            return False
                        if k == len(row_dict[i][j]) - 2:
                            temp += 1
                    else:
                        if count > 1:
                            count = 1
                            temp += 1
                if temp > 1:
                    return False
    for i in column_dict:
        for j in column_dict[i]:
            if len(column_dict[i][j]) > 3:
                temp = 0
                count = 1
                for k in range(len(column_dict[i][j]) - 1):
                    if column_dict[i][j][k] + 1 == column_dict[i][j][k + 1]:
                        count += 1
                        if count > 3:
                            return False
                        if k == len(column_dict[i][j]) - 2:
                            temp += 1
                    else:
                        if count > 1:
                            count = 1
                            temp += 1
                if temp > 1:
                    return False
    return True


def triads(field):
    row_dict = dictionary.processing(field)
    column_dict = dictionary.processing_transpose(field)
    index = -1
    for i in row_dict:
        for j in row_dict[i]:
            if len(row_dict[i][j]) >= 3:
                count = 1
                for k in range(len(row_dict[i][j]) - 1):
                    if row_dict[i][j][k] + 1 == row_dict[i][j][k + 1]:
                        count += 1
                        if count == 3:
                            index = row_dict[i][j][k]
                    else:
                        count = 1
            if index != -1:
                for n in row_dict[i][j]:
                    if (n != index):
                        field[i - 1][n] = -1
            index = -1
    index2 = -1
    field_trans = np.array(field).T
    for i in column_dict:
        for j in column_dict[i]:
            if len(column_dict[i][j]) >= 3:
                count = 1
                for k in range(len(column_dict[i][j]) - 1):
                    if column_dict[i][j][k] + 1 == column_dict[i][j][k + 1]:
                        count += 1
                        if count == 3:
                            index2 = column_dict[i][j][k]
                    else:
                        count = 1
            if index2 != -1:
                for n in column_dict[i][j]:
                    if (n != index2):
                        field_trans[i - 1][n] = -1
            index2 = -1
    return np.array(field_trans).T


# проверяем, нет ли в поле закрашеных двух клеток рядом
# если есть, выводим False и далее в main выведем, что решений нет
def field_have_solution(field):
    for i in range(len(field)):
        for j in range(len(field[0]) - 1):
            if field[i][j] == -1 and field[i][j + 1] == -1:
                return False
    for i in range(len(field) - 1):
        for j in range(len(field[0])):
            if field[i][j] == -1 and field[i + 1][j] == -1:
                return False
    return True


# делем дуальное поле: если имеем случай ..11..1..1.
# то закрашиваем все одиночные 1, иначе потом будут закрашены две 1 рядом
# тут тот же баг, что и в триадах, когда разберешься с ним там, надо и тут пофиксить
def duals(field):
    row_dict = dictionary.processing(field)
    column_dict = dictionary.processing_transpose(field)
    index1 = -1
    for i in row_dict:
        for j in row_dict[i]:
            if len(row_dict[i][j]) > 2:
                for k in range(len(row_dict[i][j]) - 1):
                    if row_dict[i][j][k] + 1 == row_dict[i][j][k + 1]:
                        index1 = row_dict[i][j][k]
                if index1 != -1:
                    for n in row_dict[i][j]:
                        if (n != index1 and n != index1 + 1):
                            field[i - 1][n] = -1
                    index1 = -1
    index2 = -1
    field_trans = np.array(field).T
    for i in column_dict:
        for j in column_dict[i]:
            if len(column_dict[i][j]) > 2:
                for k in range(len(column_dict[i][j]) - 1):
                    if column_dict[i][j][k] + 1 == column_dict[i][j][k + 1]:
                        index2 = column_dict[i][j][k]
                if index2 != -1:
                    for n in column_dict[i][j]:
                        if (n != index2 and n != index2 + 1):
                            field[i - 1][n] = -1
                    index2 = -1
    return np.array(field_trans).T


def check_all(field):
    if not evristics_check(field):
        return "no solution"
    if not field_have_solution(field):
        return "no solution"
    triad_field = triads(field)
    if not field_have_solution(triad_field):
        return "no solution"
    dual_field = duals(triad_field)
    if not field_have_solution(dual_field):
        return "no solution"
    return dual_field
