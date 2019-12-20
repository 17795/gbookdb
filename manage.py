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


@app.route('/show_book_charts', methods=['GET', 'POST'])
def show_book_charts():
    sql_query = 'select * from book order by Score desc'
    detail = select(sql_query)
    # 评分top20榜单
    detail_top = detail[:20]
    book_name = ''
    book_score = ''
    for record in detail_top:
        print(record)
        if book_name == '':
            book_name = "'" + record[1]+' ' + record[2]+"'"
            book_score = str(record[8])
        else:
            book_name = ',' + book_name
            book_name = "'" + record[1]+' ' + record[2]+"'"+book_name
            book_score = ',' + book_score
            book_score = str(record[8]) + book_score
    print(book_score)
    print(book_name)
    # 各类型平均得分柱状图
    gnere_count = {}
    gnere_sum = {}
    for record in detail:
        if record[7] in gnere_count:
            gnere_count[record[7]] += 1
            gnere_sum[record[7]] += record[8]
        else:
            gnere_count[record[7]] = 1
            gnere_sum[record[7]] = record[8]
    for i in gnere_sum.items():
        gnere_sum[i[0]] = round(float(i[1])/float(gnere_count[i[0]]), 2)
    gnere_str = ''
    gnere_score = ''
    print(gnere_sum)
    for i in gnere_sum.items():
        gnere_str = ",'"+i[0]+"'"+gnere_str
        gnere_score = ",'"+str(i[1])+"'"+gnere_score
    print(gnere_str)
    print(gnere_score)
    return render_template('book_charts.html')
    # return render_template('book_charts.html', book_name=book_name, book_score=book_score)


@app.route('/show_sale_charts', methods=['GET', 'POST'])
def show_sale_charts():
    # 用户积分排行榜
    sql_query = "SELECT `CustomerName`, RedemptionPoints FROM customer order by RedemptionPoints desc"
    detail = select(sql_query)
    # 积分top10
    detail_top = detail[:10]
    customer_name = ''
    customer_point = ''
    for record in detail_top:
        print(record)
        if customer_name == '':
            customer_name = "'" + record[0] + "'"
            customer_point = str(record[1])
        else:
            customer_name = ',' + customer_name
            customer_name = "'" + record[0] + "'" + customer_name
            customer_point = ',' + customer_point
            customer_point = str(record[1]) + customer_point
    print(customer_name)
    print(customer_point)
    # 用户订单数排行榜
    sql_query = "SELECT CustomerName,COUNT(*) FROM `customer` INNER JOIN `order` ON (`order`.CustomerID=customer.CustomerID) GROUP BY `customer`.`CustomerID` ORDER BY COUNT(*) desc"
    detail = select(sql_query)
    # 订单top10
    detail_top = detail[:10]
    active_name = ''
    active_point = ''
    for record in detail_top:
        print(record)
        if active_name == '':
            active_name = "'" + record[0] + "'"
            active_point = str(record[1])
        else:
            active_name = ',' + active_name
            active_name = "'" + record[0] + "'" + active_name
            active_point = ',' + active_point
            active_point = str(record[1]) + active_point
    print(active_name)
    print(active_point)
    # 门店销售数
    # 这个SQL我有点搞不定
    # 最后获取三个string，分别为北京、上海、深圳6-12月各自的订单数就行了，类似 '120, 132, 101, 134, 90, 230'
    # detail = select(sql_query)
    # 销售书籍类型占比饼图
    sql_query = "SELECT book.Tag,SUM(order_entry.Quantity) FROM `book` INNER JOIN `order_entry` ON (`order_entry`.ISBN=book.ISBN) GROUP BY ISBN"
    detail = select(sql_query)
    type_count = {}
    for record in detail:
        if record in type_count:
            type_count[record[0]] += int(record[1])
        else:
            type_count[record[0]] = int(record[1])
    type_str = ''
    type_count_str = ''
    for i in type_count.items():
        type_str = type_str + "'" + i[0] + "',"
        type_count_str = type_count_str + "{value:" + str(i[1]) + ", name:'" + i[0] + "'},\n"
    type_str = type_str[:-1]
    type_count_str = type_count_str[:-1]
    print(type_str)
    print(type_count_str)
    return render_template('sale_charts.html')


if __name__ == "__main__":
    app.run(debug=True)
