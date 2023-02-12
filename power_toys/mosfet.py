import json
import os

class MOSFET:
    _param_list = {
        "id"        :   None,
        "rdson"     :   None,
        "qg"        :   None,
        "footprint" :   None,
        "vbr"       :   None,
        "cosse"     :   None,
        "cosst"     :   None,
        "vgsth"     :   None,
        "qgs2"      :   None,
        "qgd"       :   None,
        "vplateau"  :   None,
        "rg"        :   None,
        "qrr"       :   None,
        "kdyn"      :   None,
        "ktemp"     :   None,
        "vgs"       :   None
    }

    def __init__(self,**kwargs) -> None:
        for key, value in kwargs.items():
            setattr(self, key, value)

    def load_from_lib(self):
        return self.from_json(self.json_filename)

    @classmethod
    def from_json(cls, json_file):
        with open(json_file) as file:
            data = json.load(file)
            return cls(**data)

    @property
    def json_filename(self):
        root = os.path.dirname(__file__)
        return f"{root}\data\mosfet\{self.id}.json"
        
    def to_json(self):
        filename = self.json_filename
        data = {key: value for key, value in self.__dict__.items()}
        with open(filename, 'w') as file:
            json.dump(data, file)