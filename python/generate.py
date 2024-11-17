#!/usr/bin/env python3

#library
import sys, re, copy, csv
#local
import data

parsedfile = sys.argv[1]

SKIP_TAGS = (data.Tag.VULGAR,data.Tag.DEROGATORY,data.Tag.PEJORATIVE,data.Tag.ETHNIC_SLUR)

LETTERS = "𐑐𐑚𐑑𐑛𐑒𐑜𐑓𐑝𐑔𐑞𐑕𐑟𐑖𐑠𐑗𐑡𐑘𐑢𐑙𐑣𐑤𐑮𐑥𐑯𐑦𐑰𐑧𐑱𐑨𐑲𐑩𐑳𐑪𐑴𐑫𐑵𐑬𐑶𐑭𐑷"
LETTER_NAMES = ("peep", "bib", "tot", "dead", "kick", "gag", "fee", "vow", "thigh", "they", "so", "zoo", "sure", "measure", "church", "judge", "yea", "woe", "hung", "haha", "loll", "roar", "mime", "nun", "if", "eat", "egg", "age", "ash", "ice", "ado", "up", "on", "oak", "wool", "ooze", "out", "oil", "ah", "awe")
LETTER_TO_NAME = {LETTERS[n]:LETTER_NAMES[n] for n in range(len(LETTERS))}
LIGATURES = {
    "𐑸":"𐑭𐑮",
    "𐑹":"𐑷𐑮",
    "𐑺":"𐑱𐑮",
    "𐑻":"𐑧𐑮",
    "𐑼":"𐑩𐑮",
    "𐑽":"𐑦𐑮",
    "𐑾":"𐑦𐑩",
    "𐑿":"𐑘𐑵"
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
            word = data.Word.read(row)
            lex['list'][word.head] = word
            if (is_skipped(word)):
                skipped += 1
                continue
            used += 1
            syntax = None
            if (word.pos is data.Pos.VERB and len (word.tags) > 0):
                syntax = (word.pos, word.form, word.tags[0]) #this may need fixing
            add_word(lex, syntax, word)
            syntax = (word.pos, word.form)
            add_word(lex, syntax, word)
            syntax = (word.pos,)
            add_word(lex, syntax, word)
            #print (lettercounts, word.shav, word.head)
    return lex

def add_word(lex, syntax, word):
    if (syntax not in lex):
        lex[syntax] = {}
    untied = untie(word.shav)
    first_letter = "1" + untied[0]
    letterset = set(word.shav) & set(LETTERS)
    lettercounts = {l:word.shav.count(l) for l in letterset}
    if (first_letter not in lex[syntax]):
        lex[syntax][first_letter] = []
    lex[syntax][first_letter].append(word)
    for letter in letterset:
        if (letter not in lex[syntax]):
            lex[syntax][letter] = []
        lex[syntax][letter].append(word)
    

def get_list(lex, syntax, letter):
    syntax_node = lex[syntax]
    list = []
    if ("1" + letter in syntax_node):
        list.extend(syntax_node["1" + letter])
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

                
lex = create_lex(parsedfile)

#generating text!
for letter in LETTERS:
    letter_word = lex['list'][LETTER_TO_NAME[letter]]
    print (letter, letter_word.head, letter_word.shav)
    list = get_list(lex, ((data.Pos.NOUN, data.Form.SINGULAR)), letter)
    for word in list[:10]:
        print (word)
    #print_syntax(lex, ((data.Pos.NOUN,)))
    ##get some common-ish nouns
    

            
        
