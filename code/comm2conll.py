# read comm XML format from stdin
# write as TSV (CoNLL) format with the following column structure
# TOKEN CHK MODERN_UNIT MODERN_VALUE SYSTEM UNIT VALUE:
# TOKEN 
# CHK: IOB (= I-,B-) + -COUNT, -COM or -MOD (note that COUNT, COM and MOD are mutually exclusive
# following columns: attributes of the first interpretation element of a COUNT 

# note that we preserve the first interpretation per count only

import sys, os,re

# *fixed* interpretation keys
keys=["modern_unit","modern_value","system","unit","value"]

for line in sys.stdin:
	if line.startswith("#P"):
		print(line,end="")
	elif line.startswith("#") or "commodities>" in line:
		pass
	else:
		line=re.sub(r"  +"," ",re.sub("<"," <",re.sub("/>"," />",re.sub(">","> ",line)))).strip()
		line=line.split()
		interpretation={}
		while(len(line)>0):
			w=line[0]
			if(w=="<count>"):
				interpretation.clear()
				interpretation["COUNT"]="B"
			elif(w=="</count>"):
				interpretation.clear()
			elif(w in ["<interpretation", "/>"]):
				pass
			elif('="' in w):
				key=re.sub(r"=.*","",w)
				if(not key in interpretation and key in keys):
					val=re.sub(r".*=","",w)
					val=re.sub(r"^['\"](.*)['\"]$",r"\1",val)
					if(len(val)==0):
						val="_"
					interpretation[key]=val
			elif "<com" in w:
				interpretation["COM"]="B"
			elif "<mod" in w:
				interpretation["MOD"]="B"
			elif w=="</com>":
				interpretation.pop("COM")
			elif w=="</mod>":
				interpretation.pop("MOD")
			else:
				# TOKEN col
				print(w,end="\t")

				# CHK col
				if("COUNT" in interpretation):
					print(interpretation["COUNT"]+"-COUNT",end="")
					if(interpretation["COUNT"]=="B"):
						interpretation["COUNT"]="I"
				elif ("COM" in interpretation):
					print(interpretation["COM"]+"-COM",end="")
					if(interpretation["COM"]=="B"):
						interpretation["COM"]="I"
				elif ("MOD" in interpretation):
					print(interpretation["MOD"]+"-MOD",end="")
					if(interpretation["MOD"]=="B"):
						interpretation["MOD"]="I"
				else:
					print("_",end="")
				
				# value cols
				for k in keys:
					if "COUNT" in interpretation:
						if k in interpretation:
							print("\t"+interpretation[k],end="")
							interpretation.pop(k)
						else:
							print("\t*",end="")
					else:
						print("\t_",end="")
				print()
			line=line[1:]
		print()
				