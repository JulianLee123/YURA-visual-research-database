#REGEX EXPRESSIONS BEING MODIFIED???

import requests
import bs4
import pandas as pd
import re

from name import Name

#Stop from hitting request cap during testing
start_idx = 0
end_idx = 169

#setup regex (need to create new string during every call)
re_name_check = r'<span class="gs_hlt">(.*?)</span>'
re_yale_check = r'<div class="gs_ai_eml">Verified email at(.*?)yale.edu</div>'
re_extract_interest = r'">(.*?)</a>'

#Update interest_col and add it to professors.csv
prof_df = pd.read_csv("professors.csv")
interest_col = []
curr_it = 1

for name in prof_df['Name'][start_idx:end_idx]:
	name = Name(name)
	print(name)
	try: 
		interests = ""
		URL = 'https://scholar.google.com/citations?view_op=search_authors&mauthors=' + name.first + '+' + name.last + '&hl=en&oi=ao'
		page = requests.get(URL)
		soup = bs4.BeautifulSoup(page.content, "html.parser")
		pot_faculty_matches = soup.findAll("div", class_="gs_ai_t") #potential faculty matches
		found_match = False
		for pot_faculty_match in pot_faculty_matches:
			try:
				print("New Faculty Match Attempt")
				name_check = False
				yale_check = False
				header_elem = pot_faculty_match.find_all("h3")
				body_elems = pot_faculty_match.find_all("div")
				#check for name match
				online_name = Name(re.findall(re_name_check,str(header_elem))[0])
				if online_name == name:
					name_check = True
				if name_check:
					print("Name Check Passed")
				else: 
					print("Online name different: " + online_name)
				#check to see if this faculty is indeed from Yale
				for body_elem in body_elems:
					if type(body_elem) == bs4.element.Tag and len(body_elem.attrs['class']) > 0 and body_elem.attrs['class'][0] == 'gs_ai_eml':
						print(body_elem)
						if len(re.findall(re_yale_check,str(body_elem))) > 0:
							yale_check = True
				#log this faculty's interest
				success = False
				if yale_check:
					print("Yale Check Passed")
				if name_check and yale_check:
					print(body_elems)
					for body_elem in body_elems:
						if type(body_elem) == bs4.element.Tag and len(body_elem.attrs['class']) > 0 and body_elem.attrs['class'][0] == 'gs_ai_int':
							interest_elems = body_elem.find_all("a")
							for interest_elem in interest_elems:
								interests += re.findall(re_extract_interest,str(interest_elem))[0] + ','
								success = True
					if success:
						interest_col.append(interests[:-1])
					break
			except Exception:
				continue #want to check other faculty matches if current potential faculty match isn't valid
	except Exception:
		pass
	finally:
		if len(interest_col) != curr_it:
			interest_col.append(None) 
		curr_it += 1

print(len(interest_col))
print(len(prof_df))
#make change to the dataframe and save changes to csv file
for i in range(start_idx,end_idx):
	if interest_col[i] != None:
		prof_df.loc[i,"Interests(GS)"] = interest_col[i]
prof_df.to_csv('professors_test.csv',index=False)
