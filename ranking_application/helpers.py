#!/usr/bin/python
# -*- coding: utf-8 -*-
def elem_count(liste):
    # Counts elemts of list and returns dict
    counted = {}
    for elem in liste:
        if elem not in counted:
            counted[elem] = 1
        else:
            counted[elem] = counted[elem] + 1
    return counted


def sort_dict(dictionary, rev=True):
    # Sorts a dict and returns key-value tuples
    sorted_dict = sorted(
        dictionary.items(),
        key=lambda k_v: k_v[1],
        reverse=rev)
    return sorted_dict


def max_key(dictionary):
    return max(dictionary, key=dictionary.get)
