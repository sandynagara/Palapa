from dataclasses import dataclass, field

import json
from ..api import endpoints
from ..memo import app_state


@dataclass
class StaticStorage:
    has_login: bool = False
    ds_landuse: dict = field(default_factory=lambda: {})
    ds_petugas_ukur: dict = field(default_factory=lambda: {})
    ds_program: dict = field(default_factory=lambda: {})
    ds_program_invent: dict = field(default_factory=lambda: {})
    ds_program_pm: dict = field(default_factory=lambda: {})
    ds_layer_definition: dict = field(default_factory=lambda: {})
    kkp_user: dict = field(default_factory=lambda: {})
    sistem_kordinat: str = "tm3"
    geoprofile: str = ""
    dt_alat_ukur: dict = field(default_factory=lambda: {})
    dt_metod_ukur: dict = field(default_factory=lambda: {})
    str_notifikasi: str = ""
    peta_bidang_id: str = ""
    is_e_sertifikat: str = ""

    user_login: dict = field(default_factory=lambda: {})

    def get_landuse_info(self):
        if not self.ds_landuse:
            response = endpoints.get_landuse_data()
            self.ds_landuse = json.loads(response.content)
        return self.ds_landuse

    def get_alat_ukur(self):
        if not self.dt_alat_ukur:
            response = endpoints.get_alat_ukur()
            self.dt_alat_ukur = json.loads(response.content)
        return self.dt_alat_ukur

    def get_metod_ukur(self):
        if not self.dt_metod_ukur:
            response = endpoints.get_metode_ukur()
            self.dt_metod_ukur = json.loads(response.content)
        return self.dt_metod_ukur

    def get_petugas_ukur(self):
        if not self.ds_petugas_ukur:
            response = endpoints.get_petugas_ukur(self.user_login.kantor.kantorID)
            self.ds_petugas_ukur = json.loads(response.content)
        return self.ds_petugas_ukur

    def get_notifikasi(self):
        if not self.str_notifikasi:
            response = endpoints.get_notifikasi_by_kantor(self.kkp_user.kantor.kantorID)
            self.str_notifikasi = response.content
        return self.str_notifikasi

    def get_program(self):
        if not self.ds_program:
            response = endpoints.get_program_by_kantor(self.kkp_user.kantor.kantorID)
            self.ds_program = json.loads(response.content)
        return self.ds_program

    def get_program(self):
        if not self.ds_program_invent:
            response = endpoints.get_program_invent_by_kantor(
                self.kkp_user.kantor.kantorID
            )
            self.ds_program_invent = json.loads(response.content)
            if not self.ds_program_invent:
                self.ds_program_invent = {"PROGRAM": [{"PROGRAMID": "", "NAMA": ""}]}
        return self.ds_program_invent
