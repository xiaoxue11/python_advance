class UpperMetaClass(type):
	def __new__(cls, classname, classparent, classattr):
		new_attr = {}
		for name, value in classattr.items():
			if not name.startswith('__')::
				new_attr[name.upper()]=value
		return type(classname, classparent, new_attr)


class Foo(object, metaclass=UpperMetaClass):
	bar='bip'