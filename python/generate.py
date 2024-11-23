#!/usr/bin/env python3

#library
import sys, re, copy, csv
#local
from data import Word, Pos, Form, Tag, Text

parsedfile = sys.argv[1]

SKIP_TAGS = (Tag.VULGAR,Tag.DEROGATORY,Tag.PEJORATIVE,Tag.ETHNIC_SLUR)

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
LETTER_TO_NAME = {LETTERS[n]:LETTER_NAMES[n] for n in range(len(LETTERS))}
ALT_LETTER_TO_NAME = {LETTERS[n]:ALT_LETTER_NAMES[n] for n in range(len(LETTERS))}
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

extras = {
    "zho": "𐑠𐑴",
    "fay": "𐑓𐑱",
    "cha": "𐑗𐑭",
    "ha-ha": "𐑣𐑭𐑣𐑭",
}
    
def is_skipped(word):
    for tag in word.tags:
        if tag in SKIP_TAGS:
            return True
    return False

def untie(word):
    untied = ""
    for letter in word:
        if (letter in LIGATURES):
            untied += LIGATURES[letter]
        elif letter in LETTERS:
            untied += letter
    return untied

"""lex[Syntax_tuple][letter or 1letter] = list of words ordered by frequency
Also lex['list'][head] = word"""
def create_lex(parsedfile):
    lex = {'list':{}}
    with open(parsedfile) as parsedhandle:
        used = 0
        skipped = 0
        parsetsv = csv.reader(parsedhandle, delimiter="\t")
        for row in parsetsv:
            word = Word.read(row)
            lex['list'][word.head] = word
            if (is_skipped(word)):
                skipped += 1
                continue
            used += 1
            syntax = None
            if (word.pos is Pos.VERB and len (word.tags) > 0):
                syntax = (word.pos, word.form, word.tags[0]) #this may need fixing
                #print(syntax)
            add_word(lex, syntax, word)
            syntax = (word.pos, word.form)
            add_word(lex, syntax, word)
            syntax = (word.pos,)
            add_word(lex, syntax, word)
            #print (lettercounts, word.shav, word.head)

    #manually added extras
    for xhead in extras:
        extra_word = Word(xhead, extras[xhead])
        lex['list'][xhead] = extra_word
        
    return lex

def add_word(lex, syntax, word):
    if (syntax not in lex):
        lex[syntax] = {}
    untied = untie(word.shav)
    first_letter = "1" + untied[0]
    letterset = set(untied) & set(LETTERS)
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
    

def get_list(lex, syntax, letter):
    syntax_node = lex[syntax]
    list = []
    if ("1" + letter in syntax_node):
        list.extend(syntax_node["1" + letter])
    if (letter in syntax_node):
        list.extend(syntax_node[letter])
    return list
    
def print_syntax(lex, syntax):
    print (",".join((e.name for e in syntax)))
    for letter in lex[syntax]:
        print (letter)
        for word in lex[syntax][letter]:
            print (word)
        
def print_lex(lex):
    for syntax in lex:
        print_syntax(lex, syntax)

def get_tagged_words(wordlist, tag, count):
    found = []
    for word in wordlist:
        if (tag in word.tags):
            found.append(word)
            if (len(found) >= count):
                return found
    return found
            
        
lex = create_lex(parsedfile)

#generating text!
for letter in LETTERS:
    letter_word = lex['list'][LETTER_TO_NAME[letter]]
    print (letter, letter_word.head, letter_word.shav)
    letter_noun_list = get_list(lex, ((Pos.NOUN, Form.SINGULAR)), letter)
    ##get some common-ish nouns
    letter_commons = {}
    for tag in (Tag.ORGANISM, Tag.ANIMAL, Tag.PEOPLE):
        tagged_list = get_tagged_words(letter_noun_list, tag, 5)
        letter_commons[tag] = tagged_list
        for word in tagged_list:
            #print (word)
            pass
            
    #get some names
    letter_name_list = get_list(lex, ((Pos.PROPER_NOUN, Form.SINGULAR)), letter)
    letter_given_list = get_tagged_words(letter_name_list, Tag.GIVEN_NAME, 10)
    for word in letter_given_list:
        #print (word)
        pass
    #get some verbs
    letter_verb_list = get_list(lex, ((Pos.VERB, Form.SINGULAR, Tag.TRANSITIVE)), letter)
    for word in letter_verb_list[:10]:
        #print (word)
        pass

    sentence = Text()
    sentence.add_word(letter_given_list[0])
    sentence.add_word(letter_verb_list[0])
    sentence.add_word(lex['list']['the'])
    sentence.add_word(letter_commons[Tag.ORGANISM][0])
    print (sentence)
    
