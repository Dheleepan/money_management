
from flask import Flask,render_template,url_for,redirect,request,flash
from collections import defaultdict
import sqlite3
con=sqlite3.connect('family_db.db',check_same_thread=False)


app = Flask(__name__)
app.secret_key = 'super secret key'

@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup',methods=['GET','POST'])
def signup():
    if request.method == 'POST':
        
        print("into sign up")
        name=request.form['name'].strip()
        username=request.form['username'].strip()
        password=request.form['password'].strip()
        familycode = request.form['family_code'].strip()
        print(name,username,password,familycode)
        query = 'insert into user (name,username,password,familycode) values(?,?,?,?);'
        con.execute(query,(name,username,password,familycode))
        con.commit()

        flash('Signed Up')
        return redirect(url_for('home'))
    return render_template('signup.html')

@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username'].strip()
        password=request.form['password'].strip()
        query = 'select password from user where username = ?;'
        result = con.execute(query,[username])
        check_password = password_extraction(result,password)
        if check_password:
            flash('login')
            query = 'select name from user where username = ?;'
            result = con.execute(query,[username])
            fetched_data = result.fetchone()
            data = extraction(fetched_data)
            return redirect(url_for('user_home',datas = data))    
            # return render_template('user_home.html',datas = data)
    return render_template('login.html')

@app.route('/user_home/<datas>',methods=['GET','POST'])
def user_home(datas):
    
    query1 = 'select username from user where name = ?'
    cursor1 = con.execute(query1,[datas])
    rows1 = cursor1.fetchone()
    username = extraction(rows1)
    
    query = 'select * from expense where username = ?;'
    cursor = con.execute(query,[username])
    rows = cursor.fetchall()
    total_value = 0
    for i in rows:
        total_value += i[2]

    return render_template('user_home.html',datas = datas, values = rows, total = total_value )


@app.route('/add_expense/<data>',methods=['GET','POST'])
def add_expense_page(data):
    print(data)
    if request.method == 'POST':
        date = request.form['date'].strip()
        item = request.form['item'].strip()
        amount = request.form['amount'].strip()
        name = data

        query1 = 'select username from user where name = ?'
        result1 = con.execute(query1,[data])
        fetched_data1 = result1.fetchone()
        username = extraction(fetched_data1)

        query2 = 'select familycode from user where name = ?'
        result2 = con.execute(query2,[data])
        fetched_data2 = result2.fetchone()
        family_code = extraction(fetched_data2)

        query3 = 'insert into expense (date,username,item,amount,familycode,name) values (?,?,?,?,?,?);'
        con.execute(query3,(date,username,item,amount,family_code,name))     
        con.commit()
        print('redirecting to main')
        return redirect(url_for('user_home',datas = data ))    
    return render_template('add_expense.html')


@app.route('/family_expense/<data>', methods = ['GET','POST'])
def family_expense(data):
    query = 'select familycode from user where name = ?'
    result = con.execute(query,[data])
    fetched_data = result.fetchone()
    family_code = extraction(fetched_data)

    query1 = 'select amount from expense where familycode = ?'
    result1 = con.execute(query1,[family_code])
    fetched_data1 = result1.fetchall()
    total_value = 0
    for i in fetched_data1:
        total_value += i[0]

    query2 = 'select name,amount from expense where familycode = ?'
    result2 = con.execute(query2,[family_code])
    fetched_data2 = result2.fetchall()
    family_user_total = defaultdict(int)
    list_of_user_amount = []
    for i in fetched_data2:
        family_user_total[i[0]] += i[1]
    print(family_user_total)
    for i,j in family_user_total.items():
        list_of_user_amount.append([i,j])
    print('finallist ______',list_of_user_amount)

    return render_template('family_expense.html', datas = data, total_value = total_value, family_name = family_code.upper(), family_user_amount = list_of_user_amount)

# def delete_expense(username):
#     qry="delete from expense where username=?;"
#     con.execute(qry,(id))
#     con.commit()

def password_extraction(result,password):
    retrived_password = ""
    for i in result:
        for j in i:
            if j.isalpha() or j.isnum():
                retrived_password += j
    if password == retrived_password:
        return True
    else:
        # print('its not matched')
        return False

def extraction(result):
    retrived_word = ""
    for i in result:
        return i

        # for j in i:
        #     if j.isalpha() or j.isdigit():
        #         retrived_word += j

# def total_expense(rows):
#     total_value = 0
#     print(rows)
#     for i in rows:
#         print(i)
#         total_value += i[2]
#     return total_value
    

if (__name__ == '__main__'):
    app.run(debug=True)