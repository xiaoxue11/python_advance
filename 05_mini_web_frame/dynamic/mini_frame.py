import re
import pymysql
from urllib.parse import unquote


URL_PATHS = {}
def router(url):
	def set_func(func):
		URL_PATHS[url] = func
		def call_func(*args, **kwargs):
			return func(*args, **kwargs)
		return call_func
	return set_func

@router(r'/index.html')
def index(ret):
	content = ''
	try:
		f = open('./templates/index.html','r')
	except:
		print('No such file')
	else:
		content = f.read()
		f.close()
		# print(content)
		# content_data = 'wait, updating'
		db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
			database='stock_db', charset='utf8')
		cursor = db.cursor()
		sql = '''select * from info'''
		cursor.execute(sql)
		data_from_mysql = cursor.fetchall()
		# print(data_from_mysql)
		cursor.close()
		db.close()
		html_template = """
			<tr>
			<td>%d</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>
			<input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
			</td>
			</tr>"""
		html = ''
		for info in data_from_mysql:
			html += html_template % (info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[7], info[1])

		content = re.sub(r'{%content%}', html, content)
		return content


@router(r'/center.html')
def center(ret):
	content = ''
	try:
		f = open('./templates/center.html','r')
	except:
		print('No such file')
	else:
		content = f.read()
		f.close()
		# print(content)
		# content_data = 'updating'
		db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
		database='stock_db', charset='utf8')
		cursor = db.cursor()
		sql = """select i.code,i.short,i.chg,i.turnover,i.price,i.highs,j.note_info from info as i inner join focus as j on i.id=j.info_id;"""
		cursor.execute(sql)
		data_from_mysql = cursor.fetchall()
		# print(data_from_mysql)
		cursor.close()
		db.close()

		html_template = """
			<tr>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>%s</td>
			<td>
			<a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
			</td>
			<td>
			<input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
			</td>
			</tr>
			"""
		html = ""

		for info in data_from_mysql:
			print(info)
			html += html_template % (info[0], info[1], info[2], info[3], info[4], info[5], info[6], info[0], info[0])

		content = re.sub(r"\{%content%\}", html, content)
		
	return content

@router(r'/add/(\d*)\.html')
def add(ret):
	# get stock code
	stock_code = ret.group(1)
	print(stock_code)
	# check whether stocke code is illegal
	db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
		database='stock_db', charset='utf8')
	cursor = db.cursor()
	sql = """select * from info where code=%s;"""
	cursor.execute(sql,(stock_code,))
	# value = cursor.fetchone()
	# print(value)
	if not cursor.fetchone():
		cursor.close()
		db.close()
		return 'The stock code is illegal'
	# check wheter add before
	sql ='''select * from info as i inner join focus as f on i.code=f.info_id where i.code=%s;'''
	cursor.execute(sql,(stock_code,))
	# if add before, do not add
	if cursor.fetchone():
		cursor.close()
		db.close()		
		return 'You have been added it, please do not it repeat'
	# if not add, then insert data to focus database
	sql = '''insert into focus (info_id) select id from info where code=%s;'''
	cursor.execute(sql,(stock_code,))
	db.commit()
	cursor.close()
	db.close()
	return 'add success'

@router(r"/del/(\d*)\.html")
def delete(ret):
	stock_code = ret.group(1)
	# connect mysql
	db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
		database='stock_db', charset='utf8')
	cursor = db.cursor()
	# 1. check whether the stocke add before
	sql = '''select * from info as i inner join focus as f on i.id=f.info_id where i.code=%s;'''
	cursor.execute(sql,(stock_code,))
	if not cursor.fetchone():
		cursor.close()
		db.close()
		return 'You are not add this stock, the action is wrong'
	# 2. if add before, the delete add
	sql = """delete from focus where info_id = (select id from info where code=%s);"""
	# print(sql)
	cursor.execute(sql,(stock_code,))
	db.commit()
	cursor.close()
	db.close()

	return "delete add succes"


@router(r"/update/(\d*)\.html")
def update(ret):
	try:
		f = open("./templates/update.html")
	except Exception as ret:
		return "%s, no such path" %ret
	else:
		# get page content
		content = f.read()
		f.close()
		# get sotck code
		stock_code = ret.group(1)
		# connect mysql
		db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
			database='stock_db', charset='utf8')
		cursor = db.cursor()
		# get data from mysql
		sql = '''select focus.info_id from focus inner join info on focus.info_id=info.id where info.code=%s;'''
		cursor.execute(sql,(stock_code,))

		stock_note_info = cursor.fetchone()
		# print(stock_note_info)
		cursor.close()
		db.close()

		# ------ replace part of contents -------
		content = re.sub(r"\{%code%\}", stock_code, content)
		content = re.sub(r"\{%note_info%\}", str(stock_note_info[0]), content)
		return content


@router(r"/update/(\d*)/(.*)\.html")
def update_note_info(ret):
	stock_code = ret.group(1)
	stock_note_info = ret.group(2)
	stock_note_info = unquote(stock_note_info)
	# connect mysql
	db = pymysql.connect(host='localhost', port=3306, user='Emily', password='1234',
		database='stock_db', charset='utf8')
	cursor = db.cursor()
	# update stock info note
	sql = '''update focus inner join info on focus.info_id=info.id set focus.note_info=%s where info_id=(select id from info where code=%s)'''
	cursor.execute(sql,(stock_note_info, stock_code))
	db.commit()
	cursor.close()
	db.close()

	return 'update success'


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
		for url, func in URL_PATHS.items():
			# print(url)
			# print(func)
			ret = re.match(url, file_name)
			# print(ret)
			if ret:
				return func(ret)
				break
		else:
			return "no such page--->%s" % file_name
	except Exception as ret:
		return "%s" % ret
	else:
		return str(env) + '-----404--->%s\n'
