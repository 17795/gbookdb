import json
from flask import Flask, render_template, request
from pymysql import *

con = connect("localhost", "root", "", "gbookdb")
app = Flask(__name__, static_url_path='')


# sql查询
def select(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    data = cur.fetchall()
    return data


def insert(sql_query):
    cur = con.cursor()
    print("OK3")
    cur.execute(sql_query)
    print("OK4")


@app.route('/')
# 路由主页
def index():
    return render_template('manage_stock.html')


@app.route('/show_stock/<argv>', methods=['GET', 'POST'])
def show_stock(argv):
    if argv == 'begin':
        return render_template('manage_stock.html')
    if argv == 'query':
        sql_query = 'select count(*) from stock'
        total = int(select(sql_query)[0][0])
        print(total)
        sql_query = 'select * from stock'
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ISBN': record[0], 'Branch': record[1], 'Stock': int(record[2])})
        data = {'total': total, 'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'newEntry':
        print('new entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Stock = request.form['Stock']
        sql_query = "INSERT INTO stock (`ISBN`,`Branch`,`Stock`) VALUES('"+ISBN+"','"+Branch+"',"+Stock+");"
        insert(sql_query)
        return render_template('manage_stock.html')
    if argv == 'editEntry':
        print('edit entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Stock = request.form['Stock']
        sql_query = "update stock set Stock="+Stock+" where ISBN='"+ISBN+"'and Branch='"+Branch+"';"
        insert(sql_query)
        return render_template('manage_stock.html')
    if argv == 'removeEntry':
        print('remove entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        sql_query = "delete from stock" + " where ISBN='"+ISBN+"'and Branch='"+Branch+"';"
        insert(sql_query)
        return render_template('manage_stock.html')


@app.route('/show_order/<argv>', methods=['GET', 'POST'])
def show_order(argv):
    if argv == 'begin':
        return render_template('manage_order.html')
    if argv == 'query':
        sql_query = 'select count(*) from purchase_order'
        total = int(select(sql_query)[0][0])
        print(total)
        sql_query = 'select * from purchase_order'
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ID': record[0], 'ISBN': record[1], 'Branch': record[2], 'Quantity': int(record[3]), 'VIP_no': record[4]})
        data = {'total': total, 'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'newEntry':
        print('new entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Quantity = request.form['Quantity']
        VIP_no = request.form['VIP_no']
        sql_query = "INSERT INTO purchase_order (`ID`,`ISBN`,`Branch`,`Quantity`,`VIP_no`)" \
                    " VALUES('" + ID + "','" + ISBN + "','" + Branch + "'," + Quantity + ",'"+VIP_no+"');"
        insert(sql_query)
        return render_template('manage_order.html')
    if argv == 'editEntry':
        print('edit entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Quantity = request.form['Quantity']
        VIP_no = request.form['VIP_no']
        sql_query = "update purchase_order set Quantity=" + Quantity+",VIP_no='" + VIP_no + "' where ID = '" + ID + "' and ISBN='" + ISBN + "'and Branch='" + Branch + "';"
        insert(sql_query)
        return render_template('manage_order.html')
    if argv == 'removeEntry':
        print('remove entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        sql_query = "delete from purchase_order" + " where ID ='" + ID + "'and ISBN='" + ISBN + "'and Branch='" + Branch + "';"
        insert(sql_query)
        return render_template('manage_order.html')


# @app.route('/show_VIP/<argv>', methods=['GET', 'POST'])
# def show_order(argv):
    # 需要设计！！！


# @app.route('/show_book/<argv>', methods=['GET', 'POST'])
# def show_order(argv):
    # 需要设计！！！


if __name__ == "__main__":
    app.run(debug=True)
