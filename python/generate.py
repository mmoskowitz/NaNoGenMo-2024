#!/usr/bin/env python3

#library
import sys, re, copy, csv
#module
import Levenshtein
#local
from data import Word, Pos, Form, Tag, Text, Punctuation, Alphabet, Lexicon, Source

lexfile = sys.argv[1]
sourcefile = sys.argv[2]
source_title_regex = sys.argv[3]
        
lex = Lexicon()
lex.read_lex(lexfile)
extrasfile = re.sub('/[^/]+$', '/extras.txt', lexfile)
lex.read_lex(extrasfile)

source = Source(lex)
source.read_file(sourcefile, source_title_regex)


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
slash = Punctuation(string="/", before=True, after=True)
exclamation = Punctuation(string="!")
comma = Punctuation(string=",")

for letter in Alphabet.LETTERS:
    print ("<h1>" + letter + "</h1>")
    title = generate_title(lex, letter)
    print ("<h2>" + title.html_text() + "</h2>")
    
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
    print ("<p>")
    print (sentence.html_text())
    print ("</p>")


for letter in Alphabet.LETTERS:
    letter_index = Alphabet.LETTERS.index(letter)
    chapter = source.chapters[letter_index]
    print ("<h2>" + chapter.parsed_title.html_text() + "</h2>")
    original_catalog = {} #head: [Word, count]
    for text in chapter.get_texts_as_list():
        for token in text.tokens:
            if (isinstance(token, Word)):
                if (token.pos not in Lexicon.OPEN_POS):
                    continue
                head = token.head.lower()
                if (head in original_catalog):
                    original_catalog[head][1] += 1
                else:
                    original_catalog[head] = [token, 1]
    replacements = {}
    pos_lists = {}
    used_replacements = set()
        
    for head in original_catalog:
        old_word = original_catalog[head][0]
        #print (old_word.shav)
        if (letter in old_word.shav and old_word.head not in used_replacements):
            used_replacements.add(head)
            continue
        #print ("replacing " + old_word.head)
        #print (old_word)
        new_word = None
        pos = old_word.pos
        form = old_word.form
        tags = old_word.tags
        letter_pos_list = []
        if ((pos,form) not in pos_lists):
            pos_lists[(pos,form)] = lex.get_list((pos,form),letter)
        letter_pos_list = pos_lists[(pos,form)]
        if (len(old_word.tags) > 0):
            letter_tag_list = []
            for tag in old_word.tags:
                letter_tag_list.extend(lex.get_tagged_words(letter_pos_list, tag, 3000))
            for word in letter_tag_list:
                if (new_word is not None):
                    continue
                if (word.head not in used_replacements):
                    new_word = word
                    replacements[head] = word
                    used_replacements.add(word.head)
                    
                else:
                    #print ("skipping " + word.head + ":" + str(used_replacements))
                    pass
        if (new_word is None):
            #print (len(letter_pos_list), "lpl")
            for word in letter_pos_list:
                #print ("checking " + word.head + " against " + str(len(used_word_heads)))
                if (new_word is not None):
                    #print ("new word set")
                    continue
                if (word.head not in used_replacements):
                    #print ("new word found")
                    new_word = word
                    replacements[head] = word
                    used_replacements.add(word.head)
                    #print ("using possed " + new_word.head)
                    #print(word)
                    #print ("is?")
                    #print(new_word)
                else:
                    #print ("skipping " +  word.head + ":" + str(used_replacements))
                    pass
                if (new_word is None):
                    new_word = old_word
                    used_replacements.add(head)
        if (head in replacements):
            #print ("replacing with " + replacements[head].head)
            pass
    if (False):
        for text in chapter.get_texts_as_list():
            for i in range(len(text.tokens)):
                token = text.tokens[i]
                if (isinstance(token, Word)):
                    old_head = text.tokens[i].head.lower()
                    if (old_head in replacements):
                        text.set(i, replacements[old_head])
    for para in chapter.parsed_texts:
        print ("<p>")
        for text in para:
            print (text.html_text())
        print ("</p>")
    
        

if (False):
    for letter in Alphabet.LETTERS:
        print (letter)
        for pos in Pos:
            count = len(lex.get_list((pos,), letter))
            if (count > 0):
                print (pos, count)
