from numpy import true_divide


class Name:

	def __init__(self, name_str):
		"""Takes a name string such as 'John Doe' or 'John Kennedy Doe'; last name must be included, middle name can be included"""
		#deals with case where middle name comes first
		if '.' in name_str.split(' ')[0]:
			name_str = name_str.split(' ', 1)[1]
		
		self.first = name_str.split(' ')[0]
		self.last = name_str.split(' ')[-1]

	def __eq__(self, other):
		if self.first == other.first and self.last == other.last:
			return True
		return False
	
	def __str__(self):
		return self.first + " " + self.last