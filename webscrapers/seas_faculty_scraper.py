#Scrapes faculty name, department, title, email, and profile URL from SEAS webpage
#Results are saved in seas_faculty.csv

import requests
import bs4
import csv
import re
import sys
from collections import namedtuple

class Professor:
	name = ''
	departments = []
	title = ''
	email = ''
	link = ''

	def get_departments_as_str(self):
		department_str = ''
		for department in self.departments:
			department_str += department + ', '
		return department_str[:-2]

	def to_dict(self):
		d = {}
		d['Name'] = self.name
		d['Departments'] = self.get_departments_as_str()
		d['Position'] = self.title
		d['Email'] = self.email
		d['Link'] = self.link
		return d

	def __str__(self):
		return str(self.title) + " " + str(self.name) + " in " + self.get_departments_as_str() + '\nemail: ' + str(self.email) + '\nURL: ' + str(self.link)

def get_seas_prof_info():
	#Get professor info and profile page URLs from the seas website: "https://seas.yale.edu/faculty-research/faculty-directory"

	#get main seas page, create soup
	URL = "https://seas.yale.edu/faculty-research/faculty-directory"
	page = requests.get(URL)
	soup = bs4.BeautifulSoup(page.content, "html.parser")
	all_seas_info = soup.find("div", class_="view-content").contents #gets info as a list

	#regex setup
	re_prof_name = r'h4>(.*?)</h4>'
	re_prof_title = r'<span class="field-content">(.*?)</span>' 
	re_profile_link = r'<a href="(.*?)"'
	re_prof_dept = r'<span class="field-content">(.*?)</span>' 
	#iterate through potential professor tiles
	professor_list = []
	for curr_bio_idx in range(0, len(all_seas_info)):
		if type(all_seas_info[curr_bio_idx]) == bs4.element.Tag:
			#found a professor tile
			prof = Professor()
			bio_info = all_seas_info[curr_bio_idx].contents
			for prof_info_idx in range(0, len(bio_info)):
				if type(bio_info[prof_info_idx]) == bs4.element.Tag and bio_info[prof_info_idx].attrs['class'][0] == 'views-field-title':
					#extract link to professor page and professor name
					for potential_link in re.findall(re_profile_link,str(bio_info[prof_info_idx].contents[1])):
						if '/faculty-research/faculty-directory/' in potential_link:
							prof.link = 'https://seas.yale.edu' + potential_link
					name = re.findall(re_prof_name,str(bio_info[prof_info_idx].contents[1]))
					if len(name) == 0:
						continue
					prof.name = name[0].strip()
				if type(bio_info[prof_info_idx]) == bs4.element.Tag and bio_info[prof_info_idx].attrs['class'][0] == 'views-field-field-person-title-value':
					#extract professor title
					position = re.findall(re_prof_title,str(bio_info[prof_info_idx].contents[1]))
					if len(position) == 0:
						continue
					prof.title = position[0].strip()
				if type(bio_info[prof_info_idx]) == bs4.element.Tag and bio_info[prof_info_idx].attrs['class'][0] == 'views-field-field-person-dept-text-value':
					#extract professor department(s)
					department_lst = re.findall(re_prof_dept,str(bio_info[prof_info_idx].contents[3]))
					if len(department_lst) == 0:
						continue
					prof.departments = department_lst[0].split(' &amp; ')
			professor_list.append(prof)
	return professor_list

def get_seas_prof_emails(professor_list):
	#Go to every professor profile and extract emails; skips professors without a profile

	#regex setup
	re_prof_email = r'/strong>(.*?)</div>'

	#go through professor profiles, extract email (rest of info extracted from main page)
	for prof in professor_list:
		try:
			page = requests.get(prof.link)
		except Exception:
			continue
		soup = bs4.BeautifulSoup(page.content, "html.parser")
		prof_info = soup.find('div', class_ = 'person-content').contents
		for prof_info_field in prof_info:
			if prof_info_field.name == 'div' and prof_info_field.attrs['class'][0] == 'person-email':
				#collect professor email
				prof.email = re.findall(re_prof_email, str(prof_info_field))
				if len(prof.email) == 0:
					prof.email = None
					continue
				prof.email = prof.email[0].strip()

def update_prof_csv(professor_list):
	#csv creation
	f = open('seas_faculty.csv', 'a+')
	dict_object = csv.DictWriter(f, fieldnames=['Name','Email','Position','Departments','Link']) 
	for prof in professor_list:
		print(prof.to_dict())
		dict_object.writerow(prof.to_dict())
	f.close()

if __name__ == "__main__":
	professor_list = get_seas_prof_info()
	get_seas_prof_emails(professor_list)
	update_prof_csv(professor_list)

	for prof in professor_list:
		print(prof)
		print("")