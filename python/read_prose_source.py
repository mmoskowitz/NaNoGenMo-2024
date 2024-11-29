#!/usr/bin/env python3

#library
import sys, re, copy, csv
from data import Word, Lexicon, Chapter, Source, Text

sourcefile = sys.argv[1]

title_regex = sys.argv[2]

lexfile = sys.argv[3]
lex = Lexicon()
lex.create_lex(lexfile)

            
source = Source(lex)
source.read_file(sourcefile, title_regex)

toc = [(chapter.title) for chapter in source.chapters]
#print ("\n".join(toc))
#print (source.chapters[3].paragraphs)
#print (source.chapters[3].parsed_texts)
