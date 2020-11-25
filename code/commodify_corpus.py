import json
import segment
import convert
import semantic
import data
import numpy as np
import re
import os
import oyaml
import gzip
import sys

from pprint import pprint 

from entry import *

from collections import defaultdict

from commodify_noDB import substitute, new_entry, label_wordlist

import argparse

########
# args #
########

args = argparse.ArgumentParser(description='Apply commodify.commodify_atf() over ATF files to produce a corpus with XML annotations. Except for the addition of a root element and the markup, the structure of the output file corresponds to the original ATF, but note that not all metadata is preserved.')
args.add_argument('SOURCE_DIR', 
					help='source directory holding the ATF files to be processed, note that we crawl all sub-folders. We process only files ending in ".atf"')
args.add_argument('TARGET_DIR',  
					help='target directory for the resulting XML files. Note that we replicate the tree structure of SOURCE_DIR and that we will not overwrite existing files')

args = args.parse_args()

#######
# def #
#######

# based on commodify.commodify_text, but less destructive to the ATF file
def commodify_atf( text ):
	"""
	Commodify a string of an ATF file and 
	return a modified file with inline (XML) markup in a shallow and opportunistic XML format.
	"""
	entries = []
	entry = new_entry()
	
	buffer="<commodities>\n"
	
	# preprocess ATF: return metadata as CoNLL comments
	lines = text.split("\n")
	text=""
	for line in lines:
		if(line.startswith("#")):
			buffer=buffer+line+"\n"
		elif(line.startswith("&")):
			buffer=buffer+(re.sub(r"^[&]","#",line))+"\n"
		elif(line.startswith("$") or line.startswith("@")): # blank lines ($) and metadata (@) skipped			
			pass
		else:
			#text=text+line+" \n "
			text=text+re.sub(r"^[\.]*[0-9][^\.]*\.\s*","",line).strip()+" \n "
	
	# Record distance from the preceding number: 
	# most commodities occur within 3 tokens of the
	# numeral
	dist_from_numeral = 0
	# Have we found a commodity in this entry yet?
	found_com = False

	text = [ re.sub(r"@[a-zA-Z]*\s*","",word) for word in text.strip().split(" ") ]
	text = [ re.sub("[#!?<>\[\]]","",word) for word in text ]
	try:
		text = segment.segment( text )
		  # File "commodify_corpus.py", line 182, in <module>
			# result=commodify_atf(buffer)
		  # File "commodify_corpus.py", line 73, in commodify_atf
			# text = segment.segment( text )
		  # File "/home/chiarcos/cdli-gh/mtaac_cdli_ur3_corpus/ur3_corpus_data/annotated/comm/cdli-accounting-viz/code/segment.py", line 45, in segment
			# for system in convert.convert_sumerian.num_systems ]):
		  # File "/home/chiarcos/cdli-gh/mtaac_cdli_ur3_corpus/ur3_corpus_data/annotated/comm/cdli-accounting-viz/code/segment.py", line 45, in <listcomp>
			# for system in convert.convert_sumerian.num_systems ]):
		  # File "/home/chiarcos/cdli-gh/mtaac_cdli_ur3_corpus/ur3_corpus_data/annotated/comm/cdli-accounting-viz/code/convert/number_system.py", line 27, in canParse
			# sign = sign[ sign.index("(") + 1 : len(sign) - 1 - sign[::-1].index(")") ]
		# ValueError: substring not found
	except ValueError:
		return None
	
	for entry_ in text:

		for string, counts in entry_:
			if True:
				entry.words_full.append(string)
				if counts is None:
					entry.counts.append( {} )
					entry.words.append(string)
				else:
					entry.counts.append( {"string":string, "readings":counts} )
					entry.words.append("###")

	result=zip(entry.words_full,label_wordlist(entry.words),entry.counts)
	result=list(map(list, result))

	# Record distance from the preceding number: 
	# most commodities occur within 3 tokens of the
	# numeral
	dist_from_numeral = None
	# was the last content token a commodity?
	found_com = False
	
	for nr,r in enumerate(result):
		s=r[0]
		l=r[1]
		c=r[2]
		if s=="\n":
			buffer=buffer+"\n"
		elif len(s)>0:
			stack=[]
			if(len(c)>0):
				buffer=buffer+"<count>"
				for i in c["readings"]:
					buffer=buffer+("<interpretation")
					for k in sorted(i.keys()):
						if k!="query":	# redundant
							buffer=buffer+(" "+k+"=\""+str(i[k])+"\"")
					buffer=buffer+("/>")
				stack.append("</count>")
				dist_from_numeral=1
				found_com=False
			if (dist_from_numeral!=None):	# return only the first after counts (here, the original commodify_text() seems to overgenerate)
				if l.endswith("_COM"):	# udu_COM
					buffer=buffer+("<com dist=\""+str(dist_from_numeral)+"\">")
					dist_from_numeral=None
					stack.append("</com>")
					found_com=True
			if (found_com):	# similar to commodify_text()
				if l.endswith("_MOD"):	# nita_MOD
					buffer=buffer+("<mod>")
					stack.append("</mod>")
				if(len(s.strip())>0):
					found_com=False	# return only first possibly modifier (different from commodify_text()
			buffer=buffer+(s)
			if(dist_from_numeral and len(s.strip())>0): 
				dist_from_numeral=+1
			for element in stack:
				buffer=buffer+element
			buffer=buffer+" "
	buffer=buffer+"\n</commodities>"
	
	return buffer


###########
# process #
###########

if not os.path.isdir(args.SOURCE_DIR):
	sys.stderr.write("warning source directory "+args.SOURCE_DIR+" not found, skipping\n")
else:
	if not os.path.isdir(args.TARGET_DIR):
		os.makedirs(args.TARGET_DIR)
	for dir, subdirs, files in os.walk(args.SOURCE_DIR):
		atfs=list(filter(lambda x: x.endswith(".atf"),files))
		if(len(atfs)>0):
			tgt=dir[len(args.SOURCE_DIR):]
			tgt=os.path.join(args.TARGET_DIR, tgt) 
			if not os.path.isdir(tgt):
				os.makedirs(tgt)
			for atf in atfs:
				output=os.path.join(tgt,re.sub(r"\.atf$","",atf)+".comm")
				atf=os.path.join(dir,atf)
				sys.stderr.write(output+" ")
				if os.path.isfile(output):
					sys.stderr.write("found, skipping\n")
				else:
					with open(atf, "r") as input:
						buffer=""
						for line in input:
							buffer=buffer+line
						buffer=buffer+"\n"

						result=commodify_atf(buffer)
						sys.stderr.write(".. ")
						if(result==None):
							sys.stderr.write("failed: parsing error\n");
						else:
							with open(output,"w") as writer:
								writer.write(result+"\n")
							if os.path.getsize(output)==0:
								sys.stderr.write("failed: empty output\n")
								os.remove(output)
							else:
								sys.stderr.write("ok\n")