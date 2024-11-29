#!/usr/bin/env python3

#library
import sys, re, copy, csv
#third-party
import wordfreq
#local
from data import Word, Pos, Form, Tag

rlsource = "/Users/marc/Documents/code/lib/readlex/kingsleyreadlexicon.tsv"
animalsource = "/Users/marc/Documents/code/NaNoGenMo-2024/sources/animals.txt"
#rlsource = "/Users/marc/Documents/code/NaNoGenMo-2024/ignore/lib/krsample.tsv"

wtsource = sys.argv[1]
corpora = {}
verb_list = {}

"""Reads in a word list and saves it to corpora"""
def read_corpus(corpora, filename, tag):
    list = []
    with open(filename) as handle:
        for line in handle:
            line = line.strip()
            if line.startswith("#"):
                continue
            list.append(line)
    corpora[tag] = list

read_corpus(corpora, animalsource, Tag.ANIMAL)

def create_rldict(rlsource):
    rldict = {}

    with open(rlsource) as rlhandle:
        rltsv = csv.reader(rlhandle, delimiter="\t")
        for row in rltsv:
            rlitem = (row[1], row[2], row[4]) #shavian, pos, freq
            pos = Pos.c5_to_pos(rlitem[1])
            rldict[row[0]] = rlitem
            rldict[(row[0], pos)] = rlitem
    return rldict

rldict = create_rldict(rlsource)

word = Word()

def get_rldict_word(rldict, word):
    head = word.head
    pos = word.pos
    if ((head, pos) in rldict):
        return rldict[(head, pos)]
    elif ((head.lower(),pos) in rldict
          and (pos is Pos.PROPER_NOUN
               or (pos in (Pos.PRONOUN, Pos.CONTRACTION)
                   and word.head.startswith("I")))):
        return rldict[(head.lower(), pos)]
    elif (head in rldict):
        return rldict[head]
    else:
        return None

"""Compile sources of information to complete our information for a word"""
def complete_word(word):
    head = word.head
    if (head is None):
        return
    if (' ' in head):
        return
    rlitem = get_rldict_word(rldict, word)
    if (rlitem is not None):
        if (word.pos is Pos.PROPER_NOUN):
            word.shav = "·" + rlitem[0]
        else:
            word.shav = rlitem[0]
    freq = wordfreq.zipf_frequency(head, "en")
    word.freq = freq
    if (word.pos is Pos.NOUN):
        #check tags
        for tag in corpora:
            if (word.head in corpora[tag]):
                word.tags.add(tag)
    if (word.shav is not None and word.freq > 0.00):
        if (word.pos is Pos.VERB):
            if (word.head not in verb_list):
                verb_list[word.head] = word
                #print ("adding " + word.head + " to verb_list: " + str(word))
        print(word)
    
"""Read a line starting with = other than Lemma: and add that information to the word"""
def parse_equals(line):
    global word
    header = re.match("=+([^=]+)=+", line).group(1)
    if (header == "English"):
        return
    if (header in Pos):
        pos = Pos(header)
        if (word.pos is not pos.UNSET and word.pos is not pos ):
            complete_word(word)
            word.form = Form.UNSET
            word.shav = None
            word.tags = set()
        word.pos = Pos(header)
        if (pos in (Pos.NOUN, Pos.PROPER_NOUN)):
            word.form = Form.SINGULAR
        elif (pos is Pos.VERB):
            word.form = Form.PLURAL
        #print (word)

"""Adds any Tag whose value is in tags to the current word"""
def add_tag_list(tags):
    global word
    for tag in tags:
        if (tag in Tag):
            tag = Tag(tag)
            tag_word(tag)
    
def tag_word(tag):
    global word
    if (tag not in word.tags):
        #print (type(word))
        #print (type(word.tags))
        word.tags.add(tag)
        
"""Read a template and add that information to the word"""
def parse_template(line):
    global word
    contents = re.match("{{([^}]*)", line).group(1)
    parts = contents.split("|")
    base = parts[0]
    if (base == "infl of"):
        if (len(parts) < 5):
            return
        root = parts[2]
        qual = parts[4]
        if (word.pos is Pos.VERB and root in verb_list):
            #print ("found root " + root)
            tags = verb_list[root].tags
            add_tag_list(tags)
        if (qual in ("s-verb-form", "st-form")):
            word.form = Form.SINGULAR
        elif (qual in ("ing-form")):
            word.form = Form.GERUND
        if (qual in ("ed-form")):
            word.form = Form.UNSET            
        else:
            pass
    elif (base == "head"):
        qual = parts[2]
        if (qual.endswith("noun form")):
            #this is probably mostly true
            word.form = Form.PLURAL
        else:
            pass
    elif (base == "lb"):
        tags = parts[2:]
        add_tag_list(tags)
    elif (base == "taxfmt"):
        tag_word(Tag.ORGANISM)
    elif (base == "given name"):
        tag_word(Tag.GIVEN_NAME)
    elif (base == "C"):
        tags = parts[2:]
        add_tag_list(tags)
    elif (base == "en-noun"):
        if (len(parts) <= 1):
            word.tags.add(Tag.COUNTABLE)
        else:
            if (parts[1] == "-"):
                word.tags.add(Tag.UNCOUNTABLE)
            elif (parts[1] == "~"):
                add_tag_list((Tag.UNCOUNTABLE, Tag.COUNTABLE))
            else:
                word.tags.add(Tag.COUNTABLE)

            if (parts[1] == "p"):
                word.form = Form.PLURAL
    else:
        #print (base + " not parsed")
        pass

        
"""Read in a line, creating a word from the information read"""
def parse_line(line):
    line = line.strip()
    global word
    if (line.startswith('=Lemma:=')):
        if (word):
            complete_word(word)
        head = line.removeprefix('=Lemma:=')
        word = Word(head=head)
    elif (line.startswith('=')):
        parse_equals(line)
    elif (line.startswith('{')):
        parse_template(line)
        

with open(wtsource) as wthandle:
    for wtline in wthandle:
        parse_line(wtline)

