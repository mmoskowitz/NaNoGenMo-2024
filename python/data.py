#!/usr/bin/env python3

#library
import sys, re, copy, csv
from dataclasses import dataclass, field
from enum import Enum, EnumMeta
from ordered_enum import OrderedEnum

class MyEnumMeta(EnumMeta):  
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        else:
            return True

class Feature(OrderedEnum, metaclass=MyEnumMeta):

    def __str__(self):
        return self.value;

    
class Pos(Feature):
    UNSET = "Unset"
    ARTICLE = "Article"
    CONJUNCTION = "Conjunction"
    DETERMINER = "Determiner"
    PREPOSITION = "Preposition"
    PRONOUN = "Pronoun"
    NUMERAL = "Numeral"
    PARTICIPLE = "Participle"
    INTERJECTION = "Interjection" 
    ADVERB = "Adverb"
    ADJECTIVE = "Adjective"
    CONTRACTION = "Contraction"
    NOUN = "Noun"
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
    EMOTIONS = "Emotions"
    OCCUPATIONS = "Occupations"
    CLOTHING = "Clothing"
    FOODS = "Foods"
    PERSONALITY = "Personality"
    ORGANISM = "organism"
    GIVEN_NAME = "given name"
    COUNTABLE = "countable"
    UNCOUNTABLE = "uncountable"

class Text:
    pass
    
@dataclass
class Token:
    text: Text = None
    index: int = 0

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
        text += str(self.string)
        if (self.after):
            text += " "
        return text
    
    def latin_text(self):
        return self.get_text()
    def shavian_text(self):
        return self.get_text()

    def html_text(self):
        return self.get_text()

    def read_text(self, text):
        self.before = text.startswith(" ")
        self.after = text.endswith(" ")
        self.string = text.strip()
        
    def __str__(self):
        return ("PUNCTUATION: '" + self.get_text() + "'")
    
@dataclass
class Word(Token):
    head: str = None
    shav: str = None
    pos: Pos = Pos.UNSET
    freq: float = 0.0
    form: Form = Form.UNSET
    tags: set[Tag] = field(default_factory=set)
    possessive: bool = False
    
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
        prev = self.get_previous()
        if (isinstance (prev, Word)):
            text += " "
        text += self.head
        if (self.head == ("a") and self.is_next_vowel()):
            text += "n"
        if (self.possessive):
            if (self.form is Form.PLURAL and self.shav[-1] in Alphabet.SIBILANTS):
                text += "'"
            else:
                text += "'s"
        if (prev is None):
            return text.capitalize()
        return text

    def is_next_vowel(self):
        next_word = self.get_next()
        if (isinstance(next_word, Word)):
            next_letter = Alphabet.untie(next_word)[0]
            if (next_letter in Alphabet.VOWELS):
                return True
        return False
    
    def shavian_text(self):
        text = ""
        if (isinstance(self.get_previous(), Word)):
            text += " "
        text += self.shav
        if (self.head == ("a") and self.is_next_vowel()):
            text += "𐑯"
        if (self.possessive):
            if (self.form is Form.PLURAL and self.shav[-1] not in Alphabet.SIBILANTS):
                if (self.shav[-1] in Alphabet.UNVOICED_CONSONANTS):
                    text += "𐑕"
                else:
                    text += "𐑟"
            else:
                if (self.shav[-1] in Alphabet.SIBILANTS):
                    text+= "𐑩𐑟"
                elif (self.shav[-1] in Alphabet.UNVOICED_CONSONANTS):
                    text += "𐑕"
                else:
                    text += "𐑟"
                    
        return text

    def html_text(self):
        return "<ruby><rb>" + self.shavian_text() + "</rb><rt>" + self.latin_text()  + "</rt></ruby>"
    

    def get_previous(self):
        if (self.text is None):
            return None
        return self.text.get_previous(self)

    def get_next(self):
        if (self.text is None):
            return None
        return self.text.get_next(self)

    
@dataclass
class Text:
    tokens: list[Token] = field(default_factory=list)

    def get_previous(self, token):
        if (token in self.tokens):
            index = token.index
            if (index > 0):
                return self.tokens[index - 1]
        return None

    def get_next(self, token):
        if (token in self.tokens):
            index = token.index
            if (len (self.tokens) > index + 1):
                return self.tokens[index + 1]
        return None

    def shavian_text(self):
        return "".join([token.shavian_text() for token in self.tokens])
    def latin_text(self):
        return "".join([token.latin_text() for token in self.tokens])

    def __str__(self):
        return self.shavian_text() +"\n" + self.latin_text()

    def html_text(self):
        return "".join([token.html_text() for token in self.tokens])

    def add(self, token):
        new_token = copy.deepcopy(token)
        new_token.text = self
        new_token.index = len(self.tokens)
        self.tokens.append(new_token)

    def set(self, index, token):
        new_token = copy.deepcopy(token)
        new_token.text = self
        new_token.index = index
        self.tokens[index] = new_token

    def is_starting(self):
        starting = True
        for token in self.tokens:
            if (isinstance(token, Word)):
                starting = False
        return starting

    def read_sentence(self, text, lex):
        latin_letters = Alphabet.LATIN_LETTERS
        space_letters = Alphabet.SPACE_LETTERS
        head_letters = Alphabet.HEAD_LETTERS
        #split into words and punctuation
        items = []
        item = ""
        for char in text:
            if (len(item) == 0):
                item += char
            elif (char in space_letters):
                if (item[0] not in head_letters):
                    item += " "
                items.append(item)
                if (item[0] in head_letters):
                    item = " "
                else:
                    item = ""
            elif (char in head_letters and item[0] in space_letters):
                item = char
            else:
                if (bool(char in head_letters) != bool(item[0] in head_letters)):
                    items.append(item)
                    item = char
                else:
                    item += char
        items.append(item)

        for item in items:
            token = lex.find_token_full(item, self.is_starting())
            if (token is not None):
                self.add(token)
            else:
                #print (item + " not found in lexicon")
                not_found_msg = "NOT_FOUND_" + item
                punc = Punctuation(before=True, string=not_found_msg, after=True)
                self.add(punc)
                pass
        
        
class Alphabet:
    LETTERS = "𐑐𐑚𐑑𐑛𐑒𐑜𐑓𐑝𐑔𐑞𐑕𐑟𐑖𐑠𐑗𐑡𐑘𐑢𐑙𐑣𐑤𐑮𐑥𐑯𐑦𐑰𐑧𐑱𐑨𐑲𐑩𐑳𐑪𐑴𐑫𐑵𐑬𐑶𐑭𐑷"
    LATIN_LETTERS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"
    HEAD_LETTERS = LATIN_LETTERS + "'"
    SPACE_LETTERS = " "
    SIBILANTS = "𐑕𐑟𐑖𐑠𐑗𐑡"
    UNVOICED_CONSONANTS = "𐑐𐑑𐑒𐑓𐑔"
    VOWELS = "𐑦𐑰𐑧𐑱𐑨𐑲𐑩𐑳𐑪𐑴𐑫𐑵𐑬𐑶𐑭𐑷"
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
    OPEN_POS = (Pos.INTERJECTION, Pos.ADVERB, Pos.ADJECTIVE, Pos.NOUN, Pos.PROPER_NOUN, Pos.VERB)

    @classmethod
    def is_skipped(cls, word):
        if ("-" in word.head):
            return True
        for tag in word.tags:
            if tag in cls.SKIP_TAGS:
                return True
        return False

    def __init__(self): 
        self.wordlist = {}
        self.lex = {}

    """lex[Syntax_tuple][letter or 1letter] = list of words ordered by frequency
    Also wordlist[head] = word"""
    def read_lex(self, parsedfile):
        lex = self.lex
        wordlist = self.wordlist
        with open(parsedfile) as parsedhandle:
            used = 0
            skipped = 0
            parsetsv = csv.reader(parsedhandle, delimiter="\t")
            for row in parsetsv:
                if ('#' in row[0] or len(row) < 3):
                    continue
                word = Word.read(row)
                if (word.head in self.wordlist):
                    current = self.wordlist[word.head]
                    if (word.pos < current.pos): #store the most closed
                        self.wordlist[word.head] = word
                else:
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

    def find_word(self, head):
        if re.match("[^" + Alphabet.LATIN_LETTERS + "]", head):
            token = Punctuation()
            token.read_text(head)
            return token
        elif (head in self.wordlist):
            return copy.deepcopy(self.wordlist[head])
        else:
            return None

    def find_token_full(self, head, starting):
        if (re.match("^[A-Z][A-Z]+$", head)):
            head = head.lower()
        if (head == "an"):
            head = "a"
        token = self.find_word(head)
        if (token is not None):
            return token
        lower_token = self.find_word(head.lower())
        if (lower_token is not None):
            if (starting):
                return lower_token
            else:
                proper_token = copy.deepcopy(lower_token)
                proper_token.head = head
                if (proper_token.freq < 5):
                    proper_token.pos = Pos.PROPER_NOUN
                proper_token.shav = "·" + proper_token.shav
                return proper_token
        #handle possessives
        if (head.endswith("'") or head.endswith("'s")):
            #find base
            poss_head = head.split("'")[0]
            poss_token = self.find_word(poss_head)
            if (poss_token is not None):
                poss_token.possessive = True
                return poss_token
            else: #proper possessives
                lower_poss_token = self.find_word(poss_head.lower())
                if (lower_poss_token is not None):
                    if (starting):
                        return lower_poss_token
                    else:
                        proper_lower_poss_token = copy.deepcopy(lower_poss_token)
                        proper_lower_poss_token.head = poss_head
                        if (proper_lower_poss_token.freq < 5):
                            proper_lower_poss_token.pos = Pos.PROPER_NOUN
                        proper_lower_poss_token.shav = "·" + proper_lower_poss_token.shav
                        return proper_lower_poss_token
        return None

    def get_list(self, syntax, letter):
        lex = self.lex
        list = []
        if (syntax not in lex):
            return list
        syntax_node = lex[syntax]
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


class Chapter:
    SENTENCE_ENDS = ".?!:"
    def __init__(self, title, text, source):
        self.title = title
        self.parsed_title = None
        self.text = text
        self.paragraphs = [] #made of [sentence = str]
        self.parsed_texts = [] #made of [text = Text]
        self.source = source
        self.decompose_text()

    def decompose_text_to_words(self):
        text = self.text
        paragraph = []
        sentence = ""
        i = 0;
        while (i < len(self.text)):
            char = text[i]
            if (char in "\n"):
                if (len(sentence) > 0):
                    paragraph.append(sentence)
                    sentence = ""
                if (len(paragraph) > 0):
                    self.paragraphs.append(paragraph)
                    paragraph = []
                
            elif (char in Chapter.SENTENCE_ENDS):
                sentence += char
                while (text[i+1] in "\"" or text[i+1] in Chapter.SENTENCE_ENDS):
                    sentence += text[i+1]
                    i += 1
                paragraph.append(sentence)
                sentence = ""
            elif (char in " "):
                if (len(sentence) > 0):
                    sentence += char
            else:
                sentence += char
            i += 1
        if (len(sentence) > 0):
            paragraph.append(sentence)
        if (len(paragraph) > 0):
            self.paragraphs.append(paragraph)

    def get_texts_as_list(self):
        list = []
        #list.append(self.parsed_title)
        for paragraph in self.parsed_texts:
            for text in paragraph:
                list.append(text)
        return list
        

    def decompose_words_to_texts(self):
        lex = self.source.lex
        for paragraph in self.paragraphs:
            parsed_para = []
            for sentence in paragraph:
                text = Text()
                text.read_sentence(sentence, lex)
                parsed_para.append(text)
            self.parsed_texts.append(parsed_para)
        parsed_title = Text()
        parsed_title.read_sentence(self.title, lex)
        self.parsed_title = parsed_title
            
    def decompose_text(self):
        self.decompose_text_to_words()
        self.decompose_words_to_texts()

            
class Source:
    def __init__(self, lexicon):
        self.chapters = []
        self.lex = lexicon

    def read_file(self, filename, title_regex):
        with open(filename) as fh:
            text = ""
            title = None
            for line in fh:
                if re.match(title_regex, line):
                    if (title is not None and len(text) > 1000): #store current chapter
                        chapter = Chapter(title, text, self)
                        self.chapters.append(chapter)
                        #print (title)

                    title  = line.strip()
                    text = ""
                else:
                    line = line.strip()
                    if (line.startswith("[")):
                        pass
                    elif (len(line) == 0):
                        text += "\n"
                    else:
                        text += " " + line
            #end of file, store last chapter
            chapter = Chapter(title, text, self)
            self.chapters.append(chapter)
