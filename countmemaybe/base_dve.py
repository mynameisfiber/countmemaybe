#!/usr/bin/env python2.7
"""
Base functions for all DVE's in the package

micha gorelick, mynameisfiber@gmail.com
http://micha.gd/
"""

import mmh3

class BaseDVE(object):
    hasher = mmh3.hash
    
    def add(self, item):
        raise NotImplemented
    
    def cardinality(self):
        raise NotImplemented
    
    def cardinality_union(self):
        raise NotImplemented
    
    def cardinality_intersection(self):
        raise NotImplemented
    
    def relative_error(self):
        raise NotImplemented
    
    def __add__(self, item):
        self.add(item)
        return self
    
    def update(self, items):
       for item in items:
           self.add(item)

    def __len__(self):
        return self.cardinality()
