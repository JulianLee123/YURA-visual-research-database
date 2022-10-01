import requests
import bs4
import pandas as pd
import re

from name import Name

#setup regex for later
re_name_check = r'<span class="gs_hlt">(.*?)</span>'
re_yale_check = r'<div class="gs_ai_eml">Verified email at(.*?)yale.edu</div>'
re_extract_interest = r'">(.*?)</a>'

#Update interest_col and add it to professors.csv
prof_df = pd.read_csv("professors.csv")
interest_col = []
for name in prof_df['Name']:
	name = Name(name)
	try: 
		interests = ""
		URL = 'https://scholar.google.com/citations?view_op=search_authors&mauthors=' + name.first + '+' + name.last + '&hl=en&oi=ao'
		page = requests.get(URL)
		soup = bs4.BeautifulSoup(page.content, "html.parser")
		pot_faculty_matches = soup.findAll("div", class_="gs_ai_t") #potential faculty matches
		for pot_faculty_match in pot_faculty_matches:
			name_check = False
			yale_check = False
			header_elem = pot_faculty_match.find_all("h3")
			body_elems = pot_faculty_match.find_all("div")
			#check for name match
			online_name = Name(re.findall(re_name_check,str(header_elem))[0])
			if online_name == name:
				name_check = True
			#check to see if this faculty is indeed from Yale
			for body_elem in body_elems:
				if type(body_elem) == bs4.element.Tag and len(body_elem.attrs['class']) > 0 and body_elem.attrs['class'][0] == 'gs_ai_eml':
					if len(re.findall(re_yale_check,str(body_elem))) > 0:
						re_yale_check = True
			#log this faculty's interest
			success = False
			if name_check and re_yale_check:
				#print(body_elems)
				for body_elem in body_elems:
					if type(body_elem) == bs4.element.Tag and len(body_elem.attrs['class']) > 0 and body_elem.attrs['class'][0] == 'gs_ai_int':
						interest_elems = body_elem.find_all("a")
						for interest_elem in interest_elems:
							interests += re.findall(re_extract_interest,str(interest_elem))[0] + ', '
							success = True
			if success:
				interest_col.append(interests[:-1])
			else:
				interest_col.append(None)
	except Exception:
		interest_col.append(None)
	break

#make change to the dataframe and save changes to csv file
prof_df["Interests"] = interest_col
prof_df.to_csv('professors_test.csv')