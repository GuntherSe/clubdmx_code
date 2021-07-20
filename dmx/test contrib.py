#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Test Contrib

contrib = [[1, 49, 1562493501.9602401],
           [2, 145, 1562493501.9602401],
           [1, 49, 1562493501.9602401],
           [2, 145, 1562493501.9602401]
           ]

cl = [1,49]

check = False
for elem in contrib:
    el = elem[:-1]
    if cl == el:
        check = True

print ("check: ", check)


