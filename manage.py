import json
from flask import Flask, render_template, request
from pymysql import *

con = connect("localhost", "root", "Ilovemtg", "gbookdb")

app = Flask(__name__, static_url_path='')


# sql查询
def select(sql_query):
    cur = con.cursor()
    print("OK")
    cur.execute(sql_query)
    print("OK2")
    data = cur.fetchall()
    # print(data)
    return data


def insert(sql_query):
    cur = con.cursor()
    print("OK3")
    cur.execute(sql_query)
    con.commit()
    print("OK4")


@app.route('/')
# 路由主页
def index():
    return render_template('manage_book.html', var = 'begin')


@app.route('/show_stock/<argv>', methods=['GET', 'POST'])
def show_stock(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM stock'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * FROM stock'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM stock WHERE ISBN = '"+info[0]+"' and Branch = '"+info[1]+"';"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM stock WHERE ISBN = '"+info[0]+"' and Branch = '"+info[1]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ISBN': record[0], 'Branch': record[1], 'Stock': int(record[2])})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_stock.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Stock = request.form['Stock']
        sql_query = "INSERT INTO stock (`ISBN`,`Branch`,`Stock`) VALUES('"+ISBN+"','"+Branch+"',"+Stock+");"
        insert(sql_query)
        return render_template('manage_stock.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Stock = request.form['Stock']
        sql_query = "UPDATE stock SET Stock="+Stock+" WHERE ISBN='"+ISBN+"'and Branch='"+Branch+"';"
        insert(sql_query)
        return render_template('manage_stock.html', var = 'query+all')
    if argv == 'removeEntry':
        print('remove entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        sql_query = "DELETE FROM stock" + " WHERE ISBN='"+ISBN+"'and Branch='"+Branch+"';"
        insert(sql_query)
        return render_template('manage_stock.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        return render_template('manage_stock.html', var = 'query+'+ISBN+'+'+Branch)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_stock.html', var = 'query+:'+SQL)


@app.route('/show_order/<argv>', methods=['GET', 'POST'])
def show_order(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM purchase_order'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * FROM purchase_order'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM purchase_order WHERE ID = '"+info[0]+"' and ISBN = '"+info[1]+"' and Branch = '"+info[2]+"';"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM purchase_order WHERE ID = '"+info[0]+"' and ISBN = '"+info[1]+"' and Branch = '"+info[2]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ID': record[0], 'ISBN': record[1], 'Branch': record[2], 'Quantity': int(record[3]), 'CustomerID': record[4]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Quantity = request.form['Quantity']
        CustomerID = request.form['CustomerID']
        sql_query = "INSERT INTO purchase_order (`ID`,`ISBN`,`Branch`,`Quantity`,`CustomerID`)" \
                    " VALUES('" + ID + "','" + ISBN + "','" + Branch + "'," + Quantity + ",'"+CustomerID+"');"
        insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        Quantity = request.form['Quantity']
        CustomerID = request.form['CustomerID']
        sql_query = "UPDATE purchase_order SET ID = '" + ID + "'"
        if Quantity != "":
            sql_query += ", Quantity='" + Quantity + "'"
        if CustomerID != "": 
            ", CustomerID='" + CustomerID + "'"
        sql_query += " WHERE ID = '" + ID + "' and ISBN = '" + ISBN + "'and Branch = '" + Branch + "';"
        insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'removeEntry':
        print('remove entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        sql_query = "DELETE FROM purchase_order" + " WHERE ID ='" + ID + "'and ISBN='" + ISBN + "'and Branch='" + Branch + "';"
        insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        ID = request.form['ID']
        ISBN = request.form['ISBN']
        print(ISBN)
        Branch = request.form['Branch']
        return render_template('manage_order.html', var = 'query+'+ID+'+'+ISBN+'+'+Branch)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_order.html', var = 'query+:'+SQL)


@app.route('/show_book/<argv>', methods=['GET', 'POST'])
def show_book(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM book'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * from book'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM book where ISBN = '"+info[0]+"';" 
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "select * from book where ISBN = '"+info[0]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ISBN': record[0], 'BookName': record[1], 'Publisher': record[2], 'Ptime': record[3], 'Price': record[4], 'ChineseIntro': record[5], 'EnglishIntro': record[6], 'Score': record[7]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        # print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_book.html', var = "query+all")
    if argv == 'newEntry':
        print('new entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        BookName = request.form['BookName']
        Publisher = request.form['Publisher']
        Ptime = request.form['Ptime']
        Price = request.form['Price']
        ChineseIntro = request.form['ChineseIntro']
        EnglishIntro = request.form['EnglishIntro']
        Score = request.form['Score']
        sql_query = "INSERT INTO book (`ISBN`,`BookName`,`Publisher`,`Ptime`,`Price`,`ChineseIntro`,`EnglishIntro`,`Score`)" \
                    " VALUES('" + ISBN + "','" + BookName + "','" + Publisher + "','"+ Ptime + "','" + Price + "','" + ChineseIntro + "','" + EnglishIntro + "','" + Score +"');"
        insert(sql_query)
        return render_template('manage_book.html', var = "query+all")
    if argv == 'editEntry':
        print('edit entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        BookName = request.form['BookName']
        Publisher = request.form['Publisher']
        Ptime = request.form['Ptime']
        Price = request.form['Price']
        ChineseIntro = request.form['ChineseIntro']
        EnglishIntro = request.form['EnglishIntro']
        Score = request.form['Score']
        sql_query = "UPDATE book SET ISBN = '" + ISBN + "' "
        if BookName != "":
            sql_query += ", `BookName` = '" + BookName +"' "
        if Publisher != "":
            sql_query += ", `Publisher` = '" + Publisher +"' "
        if Ptime !="":
            sql_query += ", `Ptime` = '" + Ptime +"' "
        if Price != "":
            sql_query += ", `Price` = '" + Price +"' "
        if ChineseIntro != "":
            sql_query += ", `ChineseIntro` = '" + ChineseIntro +"' "
        if EnglishIntro != "":
            sql_query += ", `EnglishIntro` = '" + EnglishIntro +"' "
        if Score !="":
            sql_query += ", `Score` = '" + Score +"' "
        sql_query += "where `ISBN` = '" + ISBN + "';"
        insert(sql_query)
        return render_template('manage_book.html', var = "query+all")
    if argv == 'removeEntry':
        print('remove entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        sql_query = "DELETE FROM book" + " WHERE ISBN='" + ISBN + "';"
        insert(sql_query)
        return render_template('manage_book.html', var = "query+all")
    if argv == 'searchEntry':
        print('search entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        return render_template('manage_book.html', var = 'query+'+ISBN)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_book.html', var = 'query+:'+SQL)


@app.route('/show_customer/<argv>', methods=['GET', 'POST'])
def show_customer(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM customer'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * FROM customer'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM customer WHERE CustomerID = "+info[0]+";"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM customer WHERE CustomerID = "+info[0]+";"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'CustomerID': record[0], 'CustomerName': record[1], 'Discount': record[2], 'Password': record[3]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_customer.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        CustomerName = request.form['CustomerName']
        print(CustomerName)
        Discount = request.form['Discount']
        Password = request.form['Password']
        sql_query = "INSERT INTO customer(`CustomerName`,`Discount`,`Password`) VALUES('"+CustomerName+"','"+Discount+"','"+Password+"');"
        print(sql_query)
        insert(sql_query)
        return render_template('manage_customer.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        CustomerID = request.form['CustomerID']
        print(CustomerID)
        CustomerName = request.form['CustomerName']
        Discount = request.form['Discount']
        Password = request.form['Password']
        sql_query = "UPDATE customer SET `CustomerID` = '" + CustomerID +"' "
        if CustomerName != "":
            sql_query += ", `CustomerName` = '" + CustomerName +"' "
        if Discount != "":
            sql_query += ", `Discount` = " + Discount +" "
        if Password !="":
            sql_query += ", `Password` = '" + Password +"' "
        sql_query += "where `CustomerID` = " + CustomerID + ";"
        insert(sql_query)
        return render_template('manage_customer.html', var = 'query+all')
    if argv == 'removeEntry':
        print('remove entry!')
        CustomerID = request.form['CustomerID']
        print(CustomerID)
        sql_query = "DELETE FROM customer" + " WHERE CustomerID=" + CustomerID+ ";"
        insert(sql_query)
        sql_query = "SELECT max(CustomerID) FROM customer"
        curr = int(select(sql_query)[0][0])
        print(curr)
        sql_query = "ALTER TABLE customer AUTO_INCREMENT = " + str(curr)
        insert(sql_query)
        return render_template('manage_customer.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        CustomerID = request.form['CustomerID']
        print(CustomerID)
        return render_template('manage_customer.html', var = 'query+'+CustomerID)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_customer.html', var = 'query+:'+SQL)


@app.route('/show_author/<argv>', methods=['GET', 'POST'])
def show_author(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM author'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * FROM author'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM author WHERE ISBN LIKE '"+info[0]+"' and Author LIKE '"+info[1]+"';"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM author WHERE ISBN LIKE '"+info[0]+"' and Author LIKE '"+info[1]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ISBN': record[0], 'Author': record[1]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Author = request.form['Author']
        sql_query = "INSERT INTO stock (`ISBN`,`Author`) VALUES('"+ISBN+"','"+Author+");"
        insert(sql_query)
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'removeEntry':
        print('remove entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Author = request.form['Author']
        sql_query = "DELETE FROM stock" + " WHERE ISBN='"+ISBN+"'and Author='"+Author+"';"
        insert(sql_query)
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Author = request.form['Author']
        return render_template('manage_author.html', var = 'query+'+ISBN+'+'+Author)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_author.html', var = 'query+:'+SQL)




if __name__ == "__main__":
    app.run(debug=True)
