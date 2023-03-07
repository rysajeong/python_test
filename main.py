import pymssql
import pyodbc

from flask import Flask, request
from config import *


conn = pymssql.connect(host=sql['host'],
					   user=sql['user'],
					   password=sql['password'],
					   database=sql['database'])
# conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+ sql['host'] +';DATABASE='+ sql['database'] +';UID='+ sql['user'] +';PWD='+ sql['password']+';Trusted_Connection=no;')
cursor = conn.cursor()


app = Flask(__name__)


@app.route('/')
def userList():
	cursor.execute(f'{select_sql} where status={STATUS_ACTIVE};')
	users = cursor.fetchall()
	result_data = []
	for user in users:
		result_data.append({'id': user[0],
							'status': user[1],
							'login_id': user[2].strip(),
							'email': user[3].strip(),
							'nickname': user[5]
							})

	result = {
		'users': result_data,
		'result_code': RESULT_CODE['SUCCESS'][0],
		'result_msg': RESULT_CODE['SUCCESS'][1]
	}
	return result

@app.route('/<int:user_id>')
def userInfo(user_id):
	cursor.execute(f"{select_sql} where id='{user_id}' and status>={STATUS_INACTIVE};")
	user = cursor.fetchone()

	if user is not None:
		result_data = {
			'id': user[0],
			'status': user[1],
			'login_id': user[2].strip(),
			'email': user[3].strip(),
			'nickname': user[5],
			'created_at': user[6],
			'updated_at': user[7]
		}
		result_code = RESULT_CODE['SUCCESS'][0]
		result_msg = RESULT_CODE['SUCCESS'][1]
	else:
		result_data = None
		result_code = RESULT_CODE['DATA_DOES_NOT_EXIST'][0]
		result_msg = RESULT_CODE['DATA_DOES_NOT_EXIST'][1]

	result = {
		'user': result_data,
		'result_msg': result_msg,
		'result_code': result_code
	}
	return result

@app.route('/<int:user_id>', methods=['DELETE'])
def userDelete(user_id):
	cursor.execute(f"{select_sql} where id='{user_id}' and status>={STATUS_ACTIVE};")
	user = cursor.fetchone()

	if user is not None:
		sql = f"""UPDATE {table_name} SET status={STATUS_DELETE} WHERE id='{user_id}';"""
		cursor.execute(sql)
		conn.commit()
		conn.close()

		result_code = RESULT_CODE['SUCCESS'][0]
		result_msg = RESULT_CODE['SUCCESS'][1]
	else:
		result_code = RESULT_CODE['DATA_DOES_NOT_EXIST'][0]
		result_msg = RESULT_CODE['DATA_DOES_NOT_EXIST'][1]

	result = {
		'result_msg': result_msg,
		'result_code': result_code
	}
	return result

@app.route('/', methods=['POST'])
def signUp():
	data = request.get_json()
	cursor.execute(f"{select_sql} where login_id='{data['login_id']}' and status>={STATUS_INACTIVE};")
	user = cursor.fetchone()

	login_id = data['login_id']
	email = data['email']
	password = data['password']
	nickname = data['nickname']

	if user is None:
		sql = f"""IF NOT EXISTS(SELECT login_id FROM {table_name} 
					WHERE login_id='{login_id} and status>={STATUS_INACTIVE}')
					{insert_sql} ([login_id],[email],[password],[nickname],[created_at],[updated_at])
					VALUES ('{login_id}', '{email}', '{password}', '{nickname}', GETDATE(), GETDATE())"""
		cursor.execute(sql)
		conn.commit()

		cursor.execute(f"{select_sql} where login_id='{login_id}' and status>={STATUS_INACTIVE};")
		user = cursor.fetchone()

		result_data = {
			'id': user[0],
			'status': user[1],
			'login_id': user[2].strip(),
			'email': user[3].strip(),
			'nickname': user[5]
		}
		result_code = RESULT_CODE['SUCCESS'][0]
		result_msg = RESULT_CODE['SUCCESS'][1]
	else:
		result_data = None
		result_code = RESULT_CODE['ID_DUPLICATE'][0]
		result_msg = RESULT_CODE['ID_DUPLICATE'][1]

	result = {
		'result_msg': result_msg,
		'result_code': result_code,
		'user': result_data
	}
	return result

@app.route('/<int:user_id>', methods=['PUT'])
def userUpdate(user_id):
	data = request.get_json()
	cursor.execute(f"{select_sql} where id='{user_id}' and status>={STATUS_INACTIVE};")
	user = cursor.fetchone()

	login_id = data['login_id']
	email = data['email']
	password = data['password']
	nickname = data['nickname']

	if user is not None:
		cursor.execute(f"{select_sql} WHERE login_id='{login_id}' and status>={STATUS_INACTIVE} and id NOT IN ({user_id})")
		row = cursor.fetchone()

		if row is not None:
			result = {
				'result_code': RESULT_CODE['ID_DUPLICATE'][0],
				'result_msg': RESULT_CODE['ID_DUPLICATE'][1]
			}
			return result

		sql = f"""{update_sql} 
					SET login_id='{login_id}', email='{email}', password='{password}' , nickname='{nickname}', updated_at=GETDATE()
					WHERE id='{user_id}';"""
		cursor.execute(sql)
		conn.commit()

		cursor.execute(f"{select_sql} where id='{user_id}' and status>={STATUS_INACTIVE};")
		user_detail = cursor.fetchone()

		data = {
			'id': user_detail[0],
			'status': user_detail[1],
			'login_id': user_detail[2].strip(),
			'email': user_detail[3].strip(),
			'nickname': user_detail[5]
		}
		result_data = data
		result_code = RESULT_CODE['SUCCESS'][0]
		result_msg = RESULT_CODE['SUCCESS'][1]
	else:
		result_data = None
		result_code = RESULT_CODE['DATA_DOES_NOT_EXIST'][0]
		result_msg = RESULT_CODE['DATA_DOES_NOT_EXIST'][1]

	result = {
		'result_msg': result_msg,
		'result_code': result_code,
		'user': result_data
	}
	return result


if __name__ == '__main__':
	app.run(host='0.0.0.0', debug=True)