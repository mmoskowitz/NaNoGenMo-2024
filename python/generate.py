#!/usr/bin/env python3

#library
import sys, re, copy, csv
#local
from data import Word, Pos, Form, Tag, Text, Punctuation, Alphabet, Lexicon

parsedfile = sys.argv[1]
        
lex = Lexicon()
lex.create_lex(parsedfile)

#generating text!
period = Punctuation(string=".")
slash = Punctuation(None, "/", True)

for letter in Alphabet.LETTERS:
    print (letter)
    letter_name = lex.wordlist[Alphabet.get_name(letter)]
    letter_alt_name = lex.wordlist[Alphabet.get_name(letter, True)]
    title = Text()
    title.add(letter_name)
    if (letter_name is not letter_alt_name):
        title.add(slash)
        title.add(letter_alt_name)
    print (title)
    
    letter_noun_list = lex.get_list(((Pos.NOUN, Form.SINGULAR)), letter)
    #for word in letter_noun_list:
    #print (word)
    ##get some common-ish nouns
    letter_commons = {}
    for tag in (Tag.ORGANISM, Tag.ANIMAL, Tag.PEOPLE, Tag.COUNTABLE):
        tagged_list = lex.get_tagged_words(letter_noun_list, tag, 5)
        letter_commons[tag] = tagged_list
        for word in tagged_list:
            #print (word)
            pass
            
    #get some names
    letter_name_list = lex.get_list(((Pos.PROPER_NOUN, Form.SINGULAR)), letter)
    letter_given_list = lex.get_tagged_words(letter_name_list, Tag.GIVEN_NAME, 10)
    for word in letter_given_list:
        #print (word)
        pass
    #get some verbs
    letter_verb_list = lex.get_list(((Pos.VERB, Form.SINGULAR, Tag.TRANSITIVE)), letter)
    for word in letter_verb_list[:10]:
        #print (word)
        pass

    sentence = Text()
    sentence.add(letter_given_list[0])
    sentence.add(letter_verb_list[0])
    sentence.add(lex.wordlist['the'])
    sentence.add(letter_commons[Tag.PEOPLE][0])
    sentence.add(period)
    print (sentence)
    
