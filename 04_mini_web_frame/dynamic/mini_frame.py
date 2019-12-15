import re

URL_PATHS = {}
def router(url):
	def set_func(func):
		URL_PATHS[url] = func
		def call_func(*args, **kwargs):
			return func(*args, **kwargs)
		return call_func
	return set_func

@router('/index.html')
def index():
	content = ''
	try:
		f = open('./templates/index.html','r')
	except:
		print('No such file')
	else:
		content = f.read()
		f.close()
		# print(content)
		content_data = 'wait, updating'
		content = re.sub(r'{%content%}', content_data, content)
	return content


@router('/center.html')
def center():
	content = ''
	try:
		f = open('./templates/center.html','r')
	except:
		print('No such file')
	else:
		content = f.read()
		f.close()
		# print(content)
		content_data = 'updating'
		content = re.sub(r'{%content%}', content_data, content)
	return content


def application(env, start_response):
	start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])
	# if env['file_path'] == '/index.html':
	# 	return index()
	# elif env['file_path'] == '/center.html':
	# 	return center()
	# else:
	# 	return 'hello, world'
	file_name = env['file_path']
	try:
		return URL_PATHS[file_name]()
	except Exception as ret:
		return '%s'%(str(ret))