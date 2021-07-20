#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from pack import pack


# ...

@pack.route('/test')
def test():

    return "test ok"
