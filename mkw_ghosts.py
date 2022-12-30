# This is a generated file! Please edit source .ksy file and use kaitai-struct-compiler to rebuild

import kaitaistruct
from kaitaistruct import KaitaiStruct, KaitaiStream, BytesIO
from enum import Enum


class MkwGhosts(KaitaiStruct):
    class Controllers(Enum):
        wii_wheel = 0
        wii_remote = 1
        classic_controller = 2
        gamecube_controller = 3

    class Ghost(Enum):
        players_best_time = 1
        world_record_ghost = 2
        continental_record_ghost = 3
        flag_challenge_ghost = 4
        ghost_race = 6
        friend_ghost_01 = 7
        friend_ghost_02 = 8
        friend_ghost_03 = 9
        friend_ghost_04 = 10
        friend_ghost_05 = 11
        friend_ghost_06 = 12
        friend_ghost_07 = 13
        friend_ghost_08 = 14
        friend_ghost_09 = 15
        friend_ghost_10 = 16
        friend_ghost_11 = 17
        friend_ghost_12 = 18
        friend_ghost_13 = 19
        friend_ghost_14 = 20
        friend_ghost_15 = 21
        friend_ghost_16 = 22
        friend_ghost_17 = 23
        friend_ghost_18 = 24
        friend_ghost_19 = 25
        friend_ghost_20 = 26
        friend_ghost_21 = 27
        friend_ghost_22 = 28
        friend_ghost_23 = 29
        friend_ghost_24 = 30
        friend_ghost_25 = 31
        friend_ghost_26 = 32
        friend_ghost_27 = 33
        friend_ghost_28 = 34
        friend_ghost_29 = 35
        friend_ghost_30 = 36
        normal_staff_ghost = 37
        expert_staff_ghost = 38

    def __init__(self, _io, _parent=None, _root=None):
        self._io = _io
        self._parent = _parent
        self._root = _root if _root else self
        self._read()

    def _read(self):
        self.magic = (self._io.read_bytes(4)).decode(u"utf-8")
        self.finishing_time_minutes = self._io.read_bits_int_be(7)
        self.finishing_time_seconds = self._io.read_bits_int_be(7)
        self.finishing_time_milliseconds = self._io.read_bits_int_be(10)
        self.track_id = self._io.read_bits_int_be(6)
        self.unknown_1 = self._io.read_bits_int_be(2)
        self.vehicle_id = self._io.read_bits_int_be(6)
        self.character_id = self._io.read_bits_int_be(6)
        self.ghost_sent_year = self._io.read_bits_int_be(7)
        self.ghost_sent_month = self._io.read_bits_int_be(4)
        self.ghost_sent_day = self._io.read_bits_int_be(5)
        self.controller_id = KaitaiStream.resolve_enum(MkwGhosts.Controllers, self._io.read_bits_int_be(4))
        self.unknown_2 = self._io.read_bits_int_be(4)
        self.compressed_flag = self._io.read_bits_int_be(1) != 0
        self.unknown_3 = self._io.read_bits_int_be(2)
        self.ghost_type = KaitaiStream.resolve_enum(MkwGhosts.Ghost, self._io.read_bits_int_be(7))
        self.drift_type = self._io.read_bits_int_be(1) != 0
        self.unknown_4 = self._io.read_bits_int_be(1) != 0
        self._io.align_to_byte()
        self.input_data_length = self._io.read_u2be()
        self.lap_count = self._io.read_u1()
        self.lap_split_time = [None] * (5)
        for i in range(5):
            self.lap_split_time[i] = MkwGhosts.LapSplit(self._io, self, self._root)

        self.unknown_5 = self._io.read_bytes(20)
        self.country_code = self._io.read_u1()
        self.region_code = self._io.read_u1()
        self.location_code = self._io.read_u2be()
        self.unknown_6 = self._io.read_u4be()
        self.driver_mii_data = self._io.read_bytes(74)
        self.crc16_mii = self._io.read_u2be()
        self.data = self._io.read_bytes((self._io.size() - self._io.pos()))

    class LapSplit(KaitaiStruct):
        def __init__(self, _io, _parent=None, _root=None):
            self._io = _io
            self._parent = _parent
            self._root = _root if _root else self
            self._read()

        def _read(self):
            self.finishing_time_minutes = self._io.read_bits_int_be(7)
            self.finishing_time_seconds = self._io.read_bits_int_be(7)
            self.finishing_time_milliseconds = self._io.read_bits_int_be(10)
