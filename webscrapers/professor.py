class Professor:
	name = None
	departments = []
	title = ''
	email = ''
	link = ''

	@staticmethod
	def get_lst_as_str(lst):
		lst_str = ''
		for elem in lst:
			lst_str += elem + ', '
		return lst_str[:-2]

	def get_departments_as_str(self):
		return self.get_lst_as_str(self.departments)

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
