#!/usr/bin/env python3

#library
import sys, re, copy, csv
from data import Word, Lexicon

sourcefile = sys.argv[1]

title_regex = sys.argv[2]

lexfile = sys.argv[3]
lex = Lexicon()
lex.create_lex(parsedfile)

chapters = []

class Chapter:
    def __init__(self, title, text):
        self.title = title
        self.text = text


        
with open(sourcefile) as source:
    text = ""
    title = None
    for line in source:
        if re.match(title_regex, line):
            if (title is not None and len(text) > 1000): #store current chapter
                chapter = Chapter(title, text)
                chapters.append(chapter)
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
    chapter = Chapter(title, text)
    chapters.append(chapter)

toc = [(chapter.title) for chapter in chapters]
print ("\n".join(toc))
