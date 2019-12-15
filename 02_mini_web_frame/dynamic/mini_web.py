def index():
	with open('./templates/index.html','r') as f:
		content = f.read()
	return content

def application(env, start_response):
    start_response('200 OK', [('Content-Type','text/html')])
    print(env['file_path'])
    if env['file_path'] == '/index.py':
    	return index()