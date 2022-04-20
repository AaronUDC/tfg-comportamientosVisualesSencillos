

class SingletonVariables():
	
	def __new__(cls):
		if not hasattr(cls, 'instance'):
			cls.instance = super(SingletonVariables, cls).__new__(cls)
		return cls.instance
	
