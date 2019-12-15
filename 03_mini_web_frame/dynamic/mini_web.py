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
	with open('./templates/index.html','r') as f:
		content = f.read()
	return content

@router('/register.html')
def index():
	with open('./templates/register.html','r') as f:
		content = f.read()
	return content

@router('/login.html')
def index():
	with open('./templates/login.html','r') as f:
		content = f.read()
	return content

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    file_name = env['file_path']
    try:
    	return URL_PATHS[file_name]()
    except Exception as ret:
    	return '%s'%(str(ret))
    	
    	