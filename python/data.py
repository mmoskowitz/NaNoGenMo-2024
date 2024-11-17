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
    UNSET = "Unset"
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

    @classmethod
    def c5_to_pos(cls, code):
        subcode = code[0:2]
        if (subcode in C5_DICT):
            return C5_DICT[subcode]
        else:
            return Pos.UNSET
            
C5_DICT = {
    "AJ": Pos.ADJECTIVE,
    "AT": Pos.ARTICLE,
    "AV": Pos.ADVERB,
    "CJ": Pos.CONJUNCTION,
    "CR": Pos.NUMERAL,
    "DP": Pos.DETERMINER,
    "IT": Pos.INTERJECTION,
    "NN": Pos.NOUN,
    "NP": Pos.PROPER_NOUN,
    "OR": Pos.NUMERAL,
    "PN": Pos.PROPER_NOUN,
    "PO": Pos.NOUN,
    "PR": Pos.PREPOSITION,
    "PU": Pos.UNSET, #punctuation
    "UN": Pos.UNSET,
    "VB": Pos.VERB,
    "VD": Pos.VERB,
    "VH": Pos.VERB,
    "VM": Pos.VERB,
    "VV": Pos.VERB,
    "XX": Pos.ADVERB,
    "ZZ": Pos.UNSET, #letter
}

class Form(Feature):
    UNSET = "Unset"
    PLURAL = "Plural"
    SINGULAR = "Singular"
    GERUND = "Gerund"

class Tag(Feature):
    TRANSITIVE = "transitive"
    INTRANSITIVE = "intransitive"
    VULGAR = "vulgar"
    DEROGATORY = "derogatory"
    OFFENSIVE = "offensive"
    PEJORATIVE = "pejorative"
    ETHNIC_SLUR = "ethnic slur"
    
        
@dataclass
class Word:
    head: str = None
    shav: str = None
    pos: Pos = Pos.UNSET
    freq: float = 0.0
    form: Form = Form.UNSET
    tags: list[Tag] = field(default_factory=list)
    
    def __str__(self):
        return "\t".join((self.head, self.shav, self.pos.name, str(self.freq), self.form.name, ",".join((tag.name for tag in self.tags))))

    """Read in a word from the item in print(word)"""
    @classmethod
    def read(self, row):
        #head, shav, pos.name, freq, form.name, tags.names
        pos = Pos.UNSET
        if (row[2] in Pos._member_names_):
            pos = Pos[row[2]]
            freq = float(row[3])
            form = Form.UNSET
            if (row[4] in Form._member_names_):
                form = Form[row[4]]
                tags = []
                for tag in row[5].split():
                    if (tag in Tag._member_names_):
                        tags.append(Tag[tag])
            return Word(row[0], row[1], pos, freq, form, tags)
