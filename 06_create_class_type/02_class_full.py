class A:
	num = 100

def print_b(self):
	print(self.num)

@staticmethod
def print_static():
	print('This is a static method')


@classmethod
def print_classmethod(cls):
	print(cls.num)

B = type('B',(A,),{'print_b':print_b, 'print_static': print_static, 'print_classmethod': print_classmethod})

b= B()
b.print_b()
b.print_static()
b.print_classmethod()