#!/usr/bin/env python3

from dataclasses import dataclass, field
from enum import Enum, EnumMeta
import copy

class MyEnumMeta(EnumMeta):  
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

class Feature(Enum, metaclass=MyEnumMeta):

    def __str__(self):
        return self.value;

class Pos(Feature):
    ADJECTIVE = "Adjective"
    ADVERB = "Adverb"
    ARTICLE = "Article"
    CONJUNCTION = "Conjunction"
    DETERMINER = "Determiner"
    INTERJECTION = "Interjection" 
    NOUN = "Noun"
    NUMERAL = "Numeral"
    PARTICIPLE = "Participle"
    PREPOSITION = "Preposition"
    PRONOUN = "Pronoun"
    PROPER_NOUN = "Proper noun"
    VERB = "Verb"
    
        
@dataclass
class Word:
    head: str = None
    shav: str = None
    pos: Pos = Pos.NOUN
    freq: float = 0.0 
    
    def __str__(self):
        return "\t".join((self.head, self.shav, self.pos.name, str(self.freq)))
