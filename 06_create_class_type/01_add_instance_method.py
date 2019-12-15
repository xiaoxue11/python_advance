def echo_bar(self):
	print(self.bar)

Foo = type('Foo', (), {'bar': True})	

FooChild = type('FooChild',(Foo,), {'echo_bar': echo_bar})

print( hasattr(Foo, 'echo_bar'))
print( hasattr(FooChild, 'echo_bar'))