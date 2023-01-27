from typing import List, Optional

import datetime

import bson

from data.gamess_ios import GamessIO

# TODO Move the SQL database stuff from pipelines.py into this file
# TODO implement functions for interaction with MongoDB


def create_gamess_io(name: str, hashkey: str) -> GamessIO:
    gamess_io = GamessIO()
    gamess_io.name = name
    gamess_io.hashkey = hashkey

    gamess_io.save()

    return gamess_io


def find_calculation_by_hashkey(hashkey: str) -> GamessIO:
    gamess_io = GamessIO.objects(hashkey=hashkey)
    return gamess_io


def add_gamess_inp_file(hashkey: str, inp_file: str) -> GamessIO:
    gamess_io = GamessIO.objects(hashkey=hashkey)
    gamess_io.inp_file = inp_file
    gamess_io.save()

    return gamess_io


def add_gamess_out_file(hashkey: str, out_file: str) -> GamessIO:
    gamess_io = GamessIO.objects(hashkey=hashkey)
    gamess_io.out_file = out_file
    gamess_io.save()

    return gamess_io
