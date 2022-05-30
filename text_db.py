#!/usr/bin/env python3

import json


class DB:
    def __init__(self, filename):
        self.filename = filename
        self.data = json.load(open(filename))

    def save(self):
        with open(self.filename, 'wt') as outfile:
            json.dump(self.data, outfile, ensure_ascii=False, sort_keys=True, indent='\t')

    def get_collection(self, name):
        if name not in self.data:
            return []
        return self.data[name].items()

    def set_collection(self, name, value):
        self.data[name] = value

    def set_collection_value(self, name, sub_name, value):
        if name not in self.data:
            self.data[name] = dict()
        self.data[name][sub_name] = value
