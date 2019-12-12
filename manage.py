import json
from flask import Flask, render_template, request
from pymysql import *

con = connect("localhost", "root", "", "gbookdb")

app = Flask(__name__, static_url_path='')


# sql查询
def select(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    print("SELECT FROM gbookdb OK")
    data = cur.fetchall()
    # print(data)
    return data


def insert(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    con.commit()
    print("INSERT INTO gbookdb OK")


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
        # print(j_reslist)
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
            sql_query = 'SELECT COUNT(*) FROM order_entry'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT order_entry.*,order.CustomerID,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID;'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT order_entry.*,order.CustomerID,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID WHERE order.OrderID = " + info[0] + ";"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT order_entry.*,order.CustomerID,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID WHERE order.OrderID = " + info[0] + ";"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'OrderID': record[0], 'ISBN': record[1], 'Branch': record[2], 'Quantity': record[3], 'Discount': record[4], 'CustomerID': record[5], 'Date': str(record[6]), 'Message': record[7], 'Reply': record[8], 'Status': record[9]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        # print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'processEntry':
        print('process entry!')
        OrderID = request.form['OrderID']
        print(OrderID)
        Status = select("SELECT Status FROM `order` WHERE OrderID = '" + OrderID + "'")[0][0]
        if (Status == "done" or Status == "under stock"):
        	return render_template('manage_order.html', var = 'query+all')
        Entries = select("SELECT BranchID,ISBN FROM order_entry WHERE OrderID = '" + OrderID + "'")
        print(Entries)
        Quantity = []
        for Entry in Entries:
        	Quantity.append(int(select("SELECT sum(Quantity) FROM order_entry WHERE OrderID = '" + OrderID + "' and BranchID = '" + Entry[0] + "' and ISBN = '" + Entry[1] +"';")[0][0]))
        print(Quantity)
        Stock = []
        for Entry in Entries:
        	Stock.append((select("SELECT sum(Quantity) FROM stock WHERE BranchID = '" + Entry[0] + "' and ISBN = '" + Entry[1] +"';")[0][0]))
        print(Stock)
        for i in range(len(Quantity)):
        	if (Stock[i] is None or int(Stock[i]) < Quantity[i]):
        		print ("shit",Entries[i], "is under stock")
        		sql_query = "UPDATE `order` SET Status = 'under stock' WHERE OrderID = '" + OrderID + "';"
        		insert(sql_query)
        		return render_template('manage_order.html', var = 'query+all')
        for i in range(len(Quantity)):
        	sql_query = "UPDATE stock SET Quantity = " + str(int(Stock[i])-Quantity[i]) + " WHERE BranchID = '" + Entries[i][0] + "' and ISBN = '" + Entries[i][1] + "';"
        	insert(sql_query)
        	sql_query = "UPDATE `order` SET Status = 'done' WHERE OrderID = '" + OrderID + "';"
        	insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'returnEntry':
        print('return entry!')
        OrderID = request.form['OrderID']
        print(OrderID)
        Status = select("SELECT Status FROM `order` WHERE OrderID = '" + OrderID + "'")[0][0]
        sql_query = "UPDATE `order` SET Status = 'not done' WHERE OrderID = '" + OrderID + "'"
        insert(sql_query)
        if (Status != "done"):
        	print(Status)
        	return render_template('manage_order.html', var = 'query+all')
        Entries = select("SELECT BranchID,ISBN FROM order_entry WHERE OrderID = '" + OrderID + "'")
        print(Entries)
        Quantity = []
        for Entry in Entries:
        	Quantity.append(int(select("SELECT sum(Quantity) FROM order_entry WHERE OrderID = '" + OrderID + "' and BranchID = '" + Entry[0] + "' and ISBN = '" + Entry[1] +"';")[0][0]))
        print(Quantity)
        Stock = []
        for Entry in Entries:
        	Stock.append((select("SELECT sum(Quantity) FROM stock WHERE BranchID = '" + Entry[0] + "' and ISBN = '" + Entry[1] +"';")[0][0]))
        print(Stock)
        for i in range(len(Quantity)):
        	sql_query = "UPDATE stock SET Quantity = " + str(int(Stock[i])+Quantity[i]) + " WHERE BranchID = '" + Entries[i][0] + "' and ISBN = '" + Entries[i][1] + "';"
        	print(i)
        	insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'replyEntry':
        print('reply entry!')
        OrderID = request.form['OrderID']
        print(OrderID)
        Reply = request.form['Reply']
        sql_query = "UPDATE `order` SET Reply = '"+ Reply + "' WHERE OrderID ='" + OrderID + "';"
        insert(sql_query)
        return render_template('manage_order.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        OrderID = request.form['OrderID']
        print(OrderID)
        return render_template('manage_order.html', var = 'query+'+OrderID)
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
            sql_query = 'SELECT COUNT(*) FROM book INNER JOIN compose ON book.ISBN = compose.ISBN;'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT book.*, group_concat(DISTINCT compose.AuthorName) AS AuthorName FROM book INNER JOIN compose ON book.ISBN = compose.ISBN GROUP BY book.Title;'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM book where ISBN = '"+info[0]+"';" 
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT book.*,group_concat(DISTINCT compose.AuthorName) AS AuthorName FROM book INNER JOIN compose ON compose.ISBN = book.ISBN WHERE book.ISBN = '"+info[0]+"' GROUP BY book.Title;"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'ISBN': record[0], 'Title': record[1], 'Publisher': record[2], 'Ptime': record[3], 'Price': record[4], 'ChineseIntro': record[5], 'EnglishIntro': record[6], 'Score': record[8], 'AuthorName': record[9], 'Tag': record[7]})
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
        Title = request.form['Title']
        Publisher = request.form['Publisher'] 
        AuthorNames = request.form['AuthorName']
        Ptime = request.form['Ptime']
        Price = request.form['Price']
        ChineseIntro = request.form['ChineseIntro']
        EnglishIntro = request.form['EnglishIntro']
        Score = request.form['Score']
        Tag = request.form['Tag']
        sql_query = "INSERT INTO book (`ISBN`,`Title`,`Publisher`,`Ptime`,`Price`,`ChineseIntro`,`EnglishIntro`,`Score`,`Tag`)" \
                    " VALUES('" + ISBN + "','" + Title + "','" + Publisher + "','"+ Ptime + "','" + Price + "','" + ChineseIntro + "','" + EnglishIntro + "','" + Score +"','"+ Tag + "');"
        insert(sql_query)
        AuthorNames = AuthorNames.split(',')
        for AuthorName in AuthorNames:
	        sql_query = "SELECT count(*) FROM author WHERE AuthorName = '"+AuthorName+"';"
	        total = int(select(sql_query)[0][0])
	        if total == 0:
	        	sql_query = "INSERT INTO author (`AuthorName`) VALUES('"+AuthorName+"');"
	        	insert(sql_query)
	        sql_query = "INSERT INTO compose (`ISBN`,`AuthorName`) VALUES('"+ISBN+"','"+AuthorName+"');"
	        insert(sql_query)
        return render_template('manage_book.html', var = "query+all")
    if argv == 'editEntry':
        print('edit entry!')
        ISBN = request.form['ISBN']
        print(ISBN)
        Title = request.form['Title']
        Publisher = request.form['Publisher']
        Ptime = request.form['Ptime']
        Price = request.form['Price']
        ChineseIntro = request.form['ChineseIntro']
        EnglishIntro = request.form['EnglishIntro']
        Score = request.form['Score']
        Tag = request.form['Tag']
        sql_query = "UPDATE book SET ISBN = '" + ISBN + "' "
        if Title != "":
            sql_query += ", `Title` = '" + Title +"' "
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
        if Tag !="":
            sql_query += ", `Tag` = '" + Tag +"' "
        sql_query += "WHERE `ISBN` = '" + ISBN + "';"
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
            rows.append({'CustomerID': record[0], 'CustomerName': record[1], 'Password': record[2]})
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
        Password = request.form['Password']
        sql_query = "INSERT INTO customer(`CustomerName`,`Password`) VALUES('"+CustomerName+"',MD5('"+Password+"'));"
        print(sql_query)
        insert(sql_query)
        return render_template('manage_customer.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        CustomerID = request.form['CustomerID']
        print(CustomerID)
        CustomerName = request.form['CustomerName']
        Password = request.form['Password']
        RedemptionPoint = request.form['RedemptionPoint']
        sql_query = "UPDATE customer SET `CustomerID` = '" + CustomerID +"' "
        if CustomerName != "":
            sql_query += ", `CustomerName` = '" + CustomerName +"' "
        if Password !="":
            sql_query += ", `Password` = MD5('" + Password +"') "
        if RedemptionPoint != "":
            sql_query += ", `RedemptionPoint` = '" + RedemptionPoint +"' "
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
            sql_query = "SELECT COUNT(*) FROM author WHERE AuthorName LIKE '"+info[0]+"';"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM author WHERE AuthorName LIKE '"+info[0]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'AuthorName': record[0], 'AuthorIntro': record[1]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        # print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        AuthorName = request.form['AuthorName']
        print(AuthorName)
        AuthorIntro = request.form['AuthorIntro']
        sql_query = "INSERT INTO author (`AuthorName`,`AuthorIntro`) VALUES('"+AuthorName+"','"+AuthorIntro+");"
        insert(sql_query)
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        OldAuthor = request.form['OldAuthor']
        print(OldAuthor)
        AuthorName = request.form['AuthorName']
        AuthorIntro = request.form['AuthorIntro']
        if AuthorName == "":
        	AuthorName = OldAuthor
        sql_query = "UPDATE author SET AuthorName = '" + AuthorName + "' "
        if AuthorIntro != "":
        	sql_query += ", AuthorIntro = '" + AuthorIntro +"' "
        sql_query += "WHERE `AuthorName` = '" + OldAuthor + "';"
        insert(sql_query)
        return render_template('manage_author.html', var = "query+all")
    if argv == 'removeEntry':
        print('remove entry!')
        AuthorName = request.form['AuthorName']
        print(AuthorName)
        sql_query = "DELETE FROM author" + " WHERE AuthorName='"+AuthorName+"';"
        insert(sql_query)
        return render_template('manage_author.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        AuthorName = request.form['AuthorName']
        print(AuthorName)
        return render_template('manage_author.html', var = 'query+'+AuthorName)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_author.html', var = 'query+:'+SQL)


@app.route('/show_branch/<argv>', methods=['GET', 'POST'])
def show_branch(argv):
    if argv[0:5] == 'query':
        argv = argv[6:]
        if argv == 'all':
            sql_query = 'SELECT COUNT(*) FROM branch'
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = 'SELECT * FROM branch'
        elif argv[0] == ':':
            sql_query = argv[1:]
        else:
            info = argv.split('+')
            sql_query = "SELECT COUNT(*) FROM branch WHERE BranchID = '"+info[0]+"';"
            total = int(select(sql_query)[0][0])
            print(total)
            sql_query = "SELECT * FROM stock WHERE BranchID = '"+info[0]+"';"
        detail = select(sql_query)
        rows = []
        for record in detail:
            rows.append({'BranchID': record[0], 'Address': record[1], 'Tel': record[2], 'Email': record[3]})
        data = {'rows': rows}
        j_reslist = json.dumps(data)
        # print(j_reslist)
        return j_reslist
    if argv == 'begin':
        return render_template('manage_branch.html', var = 'query+all')
    if argv == 'newEntry':
        print('new entry!')
        BranchID = request.form['BranchID']
        print(BranchID)
        Address = request.form['Address']
        Tel = request.form['Tel']
        Email = request.form['Email']
        sql_query = "INSERT INTO branch (`BranchID`,`Address`,`Tel`,`Email`) VALUES('"+BranchID+"','"+Address+"','"+Tel+"','"+Email+"');"
        insert(sql_query)
        return render_template('manage_branch.html', var = 'query+all')
    if argv == 'editEntry':
        print('edit entry!')
        BranchID = request.form['BranchID']
        print(BranchID)
        Address = request.form['Address']
        Tel = request.form['Tel']
        Email = request.form['Email']
        sql_query = "UPDATE branch SET BranchID = '" + BranchID + "' "
        if Address != "":
        	sql_query += ", Address = '" + Address +"' "
        if Tel != "":
        	sql_query += ", Tel = '" + Tel +"' "
        if Email != "":
        	sql_query += ", Email = '" + Email +"' "
        sql_query += "WHERE `BranchID` = '" + BranchID + "';"
        insert(sql_query)
        return render_template('manage_branch.html', var = 'query+all')
    if argv == 'removeEntry':
        print('remove entry!')
        BranchID = request.form['BranchID']
        print(BranchID)
        sql_query = "DELETE FROM branch" + " WHERE BranchID = '"+BranchID+"';"
        insert(sql_query)
        return render_template('manage_branch.html', var = 'query+all')
    if argv == 'searchEntry':
        print('search entry!')
        BranchID = request.form['BranchID']
        print(BranchID)
        return render_template('manage_branch.html', var = 'query+'+BranchID)
    if argv == 'searchSQL':
        print('search by sql!')
        SQL = request.form['SQL']
        print(SQL)
        return render_template('manage_branch.html', var = 'query+:'+SQL)


if __name__ == "__main__":
    app.run(debug=True)
