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

rldict = {}

with open(rlsource) as rlhandle:
    rltsv = csv.reader(rlhandle, delimiter="\t")
    for row in rltsv:
        rlitem = (row[1], row[2], row[4]) #shavian, pos, freq 
        #if (row[0] in rldict):
        #    print (row[0])
        rldict[row[0]] = rlitem

word = data.Word()

"""Compile sources of information to complete our information for a word"""
def complete_word(word):
    head = word.head
    if (head is None):
        return
    if (' ' in head):
        return
    lhead = word.head.lower()
    if (head in rldict):
        word.shav = rldict[head][0]
    #elif (word.shav):
        #convert ipa
    #    pass
    elif (lhead in rldict):
        rlitem = rldict[lhead]
        if (rlitem[1] == "NP0"): #proper nouns only
            shav = rldict[lhead][0]
            if (not (shav.startswith("·"))):
                shav = "·" + shav
            word.shav = shav
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
        
        

print (len(rldict))
        
