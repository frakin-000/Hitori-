"""Модуль реализует создание словаря по полю"""
import numpy as np


def processing(field):
    dictionary = dict.fromkeys([i+1 for i in range(len(field))])
    for i in range (len(field)):
        pre_dict = dict.fromkeys(set(field[i]), list())
        for h in set(field[i]):
            pre_list = list()
            for j in range (len(field[0])):
                if h == field[i][j]:
                    pre_list.append(j)
            pre_dict[h] = pre_list
        dictionary[i+1] = pre_dict
    return dictionary

def processing_transpose(field):
    transpose_field = np.array(field).T
    return processing(transpose_field)