#!/usr/bin/env python3

#library
import sys, re, copy, csv
#module
import Levenshtein
#local
from data import Word, Pos, Form, Tag, Text, Punctuation, Alphabet, Lexicon

parsedfile = sys.argv[1]
        
lex = Lexicon()
lex.create_lex(parsedfile)


def generate_title(lex, letter):
    letter_name = lex.wordlist[Alphabet.get_name(letter)]
    letter_alt_name = lex.wordlist[Alphabet.get_name(letter, True)]
    title = Text()
    title.add(letter_name)
    if (letter_name is not letter_alt_name):
        title.add(slash)
        title.add(letter_alt_name)
    return title

def is_close(text, new_word):
    for token in text.tokens:
        if (Levenshtein.distance(token.shavian_text(), new_word.shavian_text()) < 3):
            return True
    return False

def add_new_enough_word(text, word_list):
    for word in word_list:
        if (not(is_close(text, word))):
            text.add(word)
            return
    text.add(word_list[0])


#generating text!
period = Punctuation(string=".")
slash = Punctuation(None, "/", True)
exclamation = Punctuation(string="!")
comma = Punctuation(string=",")

for letter in Alphabet.LETTERS:
    print (letter)
    title = generate_title(lex, letter)
    print (title)
    
    letter_noun_list = lex.get_list(((Pos.NOUN, Form.SINGULAR)), letter)
    ##get some common-ish nouns
    letter_commons = {}
    for tag in (Tag.ORGANISM, Tag.ANIMAL, Tag.PEOPLE, Tag.OCCUPATIONS, Tag.COUNTABLE):
        tagged_list = lex.get_tagged_words(letter_noun_list, tag, 5)
        letter_commons[tag] = tagged_list
            
    #get some names
    letter_name_list = lex.get_list(((Pos.PROPER_NOUN, Form.SINGULAR)), letter)
    letter_given_list = lex.get_tagged_words(letter_name_list, Tag.GIVEN_NAME, 10)
    #get some verbs
    letter_verb_list = lex.get_list(((Pos.VERB, Form.SINGULAR, Tag.TRANSITIVE)), letter)
    letter_adj_list = lex.get_list((Pos.ADJECTIVE,), letter)
    letter_adv_list = lex.get_list((Pos.ADVERB,), letter)

    sentence = Text()
    letter_intj_list = lex.get_list((Pos.INTERJECTION,), letter)
    if (len(letter_intj_list) > 0):
        sentence = Text()
        sentence.add(letter_intj_list[0])
        sentence.add(comma)
    sentence.add(letter_given_list[0])
    add_new_enough_word(sentence, letter_verb_list)
    sentence.add(lex.wordlist['the'])
    add_new_enough_word(sentence, letter_adv_list)
    add_new_enough_word(sentence, letter_adj_list)
    add_new_enough_word(sentence, letter_commons[Tag.OCCUPATIONS])
    sentence.add(period)
    print (sentence)
                 

if (False):
    for letter in Alphabet.LETTERS:
        print (letter)
        for pos in Pos:
            count = len(lex.get_list((pos,), letter))
            if (count > 0):
                print (pos, count)
