#!/usr/bin/env python3

#library
import sys, re, copy, csv
#third-party
import wordfreq
#local
import data

rlsource = "/Users/marc/Documents/code/lib/readlex/kingsleyreadlexicon.tsv"
#rlsource = "/Users/marc/Documents/code/NaNoGenMo-2024/ignore/lib/krsample.tsv"

wtsource = sys.argv[1]

def create_rldict(rlsource):
    rldict = {}

    with open(rlsource) as rlhandle:
        rltsv = csv.reader(rlhandle, delimiter="\t")
        for row in rltsv:
            rlitem = (row[1], row[2], row[4]) #shavian, pos, freq
            pos = data.Pos.c5_to_pos(rlitem[1])
            rldict[row[0]] = rlitem
            rldict[(row[0], pos)] = rlitem
    return rldict

rldict = create_rldict(rlsource)

word = data.Word()

def get_rldict_word(rldict, word):
    head = word.head
    pos = word.pos
    if ((head, pos) in rldict):
        return rldict[(head, pos)]
    elif (head in rldict):
        return rldict[head]
    elif ((head.lower(),pos) in rldict and pos is data.Pos.PROPER_NOUN):
        return rldict[(head.lower(), pos)]
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
        if (word.pos is data.Pos.PROPER_NOUN):
            word.shav = "." + rlitem[0]
        else:
            word.shav = rlitem[0]
    freq = wordfreq.zipf_frequency(head, "en")
    word.freq = freq
    if (word.shav is not None and word.freq > 0.00):
        print(word)
    
"""Read a line starting with = other than Lemma: and add that information to the word"""
def parse_equals(line):
    global word
    header = re.match("=+([^=]+)=+", line).group(1)
    if (header == "English"):
        return
    if (header in data.Pos):
        pos = data.Pos(header)
        if (word.pos is not pos.UNSET and word.pos is not pos ):
            complete_word(word)
            word.form = data.Form.UNSET
            word.tags = []
        word.pos = data.Pos(header)
        if (pos in (data.Pos.NOUN, data.Pos.PROPER_NOUN)):
            word.form = data.Form.SINGULAR
        elif (pos is data.Pos.VERB):
            word.form = data.Form.PLURAL
        #print (word)
    
"""Read a template and add that information to the word"""
def parse_template(line):
    global word
    contents = re.match("{{([^}]*)", line).group(1)
    parts = contents.split("|")
    base = parts[0]
    if (base == "infl of"):
        if (len(parts) < 5):
            return
        qual = parts[4] 
        if (qual in ("s-verb-form", "st-form")):
            word.form = data.Form.SINGULAR
        elif (qual in ("ing-form")):
            word.form = data.Form.GERUND
        if (qual in ("ed-form")):
            word.form = data.Form.UNSET            
        else:
            pass
    elif (base == "head"):
        qual = parts[2]
        if (qual.endswith("noun form")):
            #this is probably mostly true
            word.form = data.Form.PLURAL
        else:
            pass
    elif (base == "lb"):
        tags = parts[2:]
        for tag in tags:
            if (tag in data.Tag):
                tag = data.Tag(tag)
                if (tag not in word.tags):
                    word.tags.append(tag)
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
        word = data.Word(head=head)
    elif (line.startswith('=')):
        parse_equals(line)
    elif (line.startswith('{')):
        parse_template(line)
        

with open(wtsource) as wthandle:
    for wtline in wthandle:
        parse_line(wtline)

