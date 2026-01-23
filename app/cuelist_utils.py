#!/usr/bin/env python3
# -*- coding: utf-8 -*-
""" Cuedata Utils """

import globs

def cuedata_to_dict (vd:list) ->dict:
    """ List data in dict wandeln
    """
    return {"listnum":     vd[0],
            "fading_in":   vd[1],
            "fading_out":  vd[2],
            "is_paused":   vd[3],
            "current_id":  vd[4],
            "current_text":vd[5],
            "next_id":     vd[6],
            "next_text":   vd[7]
            }


def cuedata_view (*viewdata):
    """ Cuedata auf die Website schicken
    """
    # logger.debug (f"cue_view: {viewdata}")
    globs.sync_data.append ({"event_name":"update cueview",
                             "data": cuedata_to_dict (viewdata[1]) 
                           })
