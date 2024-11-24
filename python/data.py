#!/usr/bin/env python3

#library
import sys, re, copy, csv
from dataclasses import dataclass, field
from enum import Enum, EnumMeta

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
    CONTRACTION = "Contraction"
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
        if ('+' in code):
            return Pos.CONTRACTION
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
    "PN": Pos.PRONOUN,
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
    ANIMAL = "animal"
    PEOPLE = "People"
    OCCUPATIONS = "Occupations"
    ORGANISM = "organism"
    GIVEN_NAME = "given name"
    COUNTABLE = "countable"
    UNCOUNTABLE = "uncountable"

class Text:
    pass
    
@dataclass
class Token:
    text: Text = None

    def latin_text(self):
        return ""

    def shavian_text(self):
        return ""

@dataclass
class Punctuation(Token):
    string: str = ""
    before: bool = False # space before
    after: bool = True # space after

    def get_text(self):
        text = ""
        if (self.before):
            text += " "
        text += self.string
        if (self.after):
            text += " "
        return text
    
    def latin_text(self):
        return self.get_text()
    def shavian_text(self):
        return self.get_text()
    
    
@dataclass
class Word(Token):
    head: str = None
    shav: str = None
    pos: Pos = Pos.UNSET
    freq: float = 0.0
    form: Form = Form.UNSET
    tags: set[Tag] = field(default_factory=set)
    
    def __str__(self):
        return "\t".join((self.head, self.shav, self.pos.name, str(self.freq), self.form.name, ",".join((tag.name for tag in self.tags))))

    """Read in a word from the item in print(word)"""
    @classmethod
    def read(cls, row):
        #head, shav, pos.name, freq, form.name, tags.names
        pos = Pos.UNSET
        if (row[2] in Pos._member_names_):
            pos = Pos[row[2]]
            freq = float(row[3])
            form = Form.UNSET
            if (row[4] in Form._member_names_):
                form = Form[row[4]]
                tags = set()
                for tag in row[5].split(','):
                    if (tag in Tag._member_names_):
                        tags.add(Tag[tag])
            return Word(head=row[0], shav=row[1], pos=pos, freq=freq, form=form, tags=tags)

    def latin_text(self):
        text = ""
        if (self.text is not None and type(self.text.get_previous(self)) is Word):
            text += " "
        text += self.head
        return text

    def shavian_text(self):
        text = ""
        if (self.text is not None and type(self.text.get_previous(self)) is Word):
            text += " "
        text += self.shav
        return text
        
@dataclass
class Text:
    tokens: list[Token] = field(default_factory=list)

    def get_previous(self, token):
        if (token in self.tokens):
            index = self.tokens.index(token)
            if (index > 0):
                return self.tokens[index - 1]
        return None

    def get_next(self, token):
        if (token in self.tokens):
            index = self.tokens.index(token)
            if (len (self.tokens) > index + 1):
                return self.tokens[index + 1]
        return None

    def shavian_text(self):
        return "".join([token.shavian_text() for token in self.tokens])
    def latin_text(self):
        return "".join([token.latin_text() for token in self.tokens])

    def __str__(self):
        return self.shavian_text() +"\n" + self.latin_text()

    def add(self, token):
        new_token = copy.deepcopy(token)
        new_token.text = self
        self.tokens.append(new_token)
        
class Alphabet:
    LETTERS = "𐑐𐑚𐑑𐑛𐑒𐑜𐑓𐑝𐑔𐑞𐑕𐑟𐑖𐑠𐑗𐑡𐑘𐑢𐑙𐑣𐑤𐑮𐑥𐑯𐑦𐑰𐑧𐑱𐑨𐑲𐑩𐑳𐑪𐑴𐑫𐑵𐑬𐑶𐑭𐑷"
    LETTER_NAMES = ("peep", "bib", "tot", "dead",
                    "kick", "gag", "fee", "vow",
                    "thigh", "they", "so", "zoo",
                    "sure", "measure", "church", "judge",
                    "yea", "woe", "hung", "ha-ha",
                    "loll", "roar", "mime", "nun",
                    "if", "eat", "egg", "age",
                    "ash", "ice", "ado", "up",
                    "on", "oak", "wool", "ooze",
                    "out", "oil", "ah", "awe")
    ALT_LETTER_NAMES = ("pin", "bell", "tan", "done",
                        "key", "gill", "fay", "vie",
                        "thorn", "thou", "see", "zoo",
                        "shy", "zho", "cha", "joy",
                        "yen", "way", "song", "who",
                        "lamb", "roe", "me", "now",
                        "in", "eve", "edge", "aim",
                        "ash", "eyes", "ago", "up",
                        "on", "oath", "oomph", "ooze",
                        "ounce", "oil", "alms", "ought")
    LIGATURES = {
        "𐑸":"𐑭𐑮",
        "𐑹":"𐑷𐑮",
        "𐑺":"𐑱𐑮",
        "𐑻":"𐑳𐑮",
        "𐑼":"𐑩𐑮",
        "𐑽":"𐑦𐑮",
        "𐑾":"𐑦𐑩",
        "𐑿":"𐑘𐑵"
    }

    NAMES = {}

    @classmethod
    def get_names(cls):
        if (len(cls.NAMES) == 0):
            LETTER_TO_NAME = {cls.LETTERS[n]:cls.LETTER_NAMES[n] for n in range(len(cls.LETTERS))}
            ALT_LETTER_TO_NAME = {cls.LETTERS[n]:cls.ALT_LETTER_NAMES[n] for n in range(len(cls.LETTERS))}
            cls.NAMES[True] = ALT_LETTER_TO_NAME
            cls.NAMES[False] = LETTER_TO_NAME
        return cls.NAMES
            
    

    @classmethod
    def untie(cls, word):
        untied = ""
        for letter in word.shav:
            if (letter in cls.LIGATURES):
                untied += cls.LIGATURES[letter]
            elif letter in cls.LETTERS:
                untied += letter
        return untied

    @classmethod
    def get_name(cls, letter, is_alt=False):
        names = cls.get_names()
        return names[is_alt][letter]
        
class Lexicon:
    SKIP_TAGS = (Tag.VULGAR,Tag.DEROGATORY,Tag.PEJORATIVE,Tag.ETHNIC_SLUR)
    EXTRAS = {
        "zho": "𐑠𐑴",
        "fay": "𐑓𐑱",
        "cha": "𐑗𐑭",
        "ha-ha": "𐑣𐑭𐑣𐑭",
    }

    @classmethod
    def is_skipped(cls, word):
        for tag in word.tags:
            if tag in cls.SKIP_TAGS:
                return True
        return False

    def __init__(self): 
        self.wordlist = {}
        self.lex = {}

    """lex[Syntax_tuple][letter or 1letter] = list of words ordered by frequency
    Also wordlist[head] = word"""
    def create_lex(self, parsedfile):
        lex = self.lex
        wordlist = self.wordlist
        with open(parsedfile) as parsedhandle:
            used = 0
            skipped = 0
            parsetsv = csv.reader(parsedhandle, delimiter="\t")
            for row in parsetsv:
                word = Word.read(row)
                self.wordlist[word.head] = word
                if (Lexicon.is_skipped(word)):
                    skipped += 1
                    continue
                used += 1
                syntax = [word.pos]
                self.add_word(syntax, word)
                syntax.append(word.form)
                self.add_word(syntax, word)
                syntax.append(None)
                for tag in word.tags:
                    syntax[2] = tag
                    self.add_word(syntax, word)
                #print (lettercounts, word.shav, word.head)

        #manually added extras
        for xhead in Lexicon.EXTRAS:
            extra_word = Word(head=xhead, shav=Lexicon.EXTRAS[xhead])
            wordlist[xhead] = extra_word

    def add_word(self, arg_syntax, word):
        lex = self.lex
        syntax = tuple(arg_syntax)
        if (syntax not in lex):
            lex[syntax] = {}
        untied = Alphabet.untie(word)
        first_letter = "1" + untied[0]
        letterset = set(untied) & set(Alphabet.LETTERS)
        lettercounts = {l:untied.count(l) for l in letterset}
        if (first_letter not in lex[syntax]):
            lex[syntax][first_letter] = []
        lex[syntax][first_letter].append(word)
        for letter in letterset:
            if (letter in first_letter):
                continue
            if (letter not in lex[syntax]):
                lex[syntax][letter] = []
            lex[syntax][letter].append(word)


    def get_list(self, syntax, letter):
        lex = self.lex
        syntax_node = lex[syntax]
        list = []
        if ("1" + letter in syntax_node):
            list.extend(syntax_node["1" + letter])
        if (letter in syntax_node):
            list.extend(syntax_node[letter])
        return list

    def print_syntax(self, syntax):
        lex = self.lex
        print (",".join((e.name for e in syntax)))
        for letter in lex[syntax]:
            print (letter)
            for word in lex[syntax][letter]:
                print (word)

    def print_lex(self):
        for syntax in self.lex:
            self.print_syntax(syntax)

    def get_tagged_words(self, wordlist, tag, count):
        found = []
        for word in wordlist:
            if (tag in word.tags):
                found.append(word)
                if (len(found) >= count):
                    return found
        return found

