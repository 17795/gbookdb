from flask import *
from pymysql import *
import hashlib
import datetime
import logg

con = connect("localhost", "root", "", "gbookdb")
app = Flask(__name__, static_url_path='')
app.config['SECRET_KEY'] = 'forsession'
customer = ""


# 封装 sql 操作
def littleselect(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    tupledata = cur.fetchall()
    listdata = []
    for i in range(len(tupledata)):
        listdata.append(list(tupledata[i]))
        for j in range(len(listdata[i])):
            if isinstance(listdata[i][j], str):
                if len(listdata[i][j]) > 400:
                    listdata[i][j] = listdata[i][j][:399] + "..."
    return listdata


def select(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    logger.info(sql_query)
    data = cur.fetchall()
    return data


def insert(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    logger.info('***新增数据*** %s' % sql_query)
    con.commit()


# 积分转化为折扣
def rp2dis(rp):
    if rp < 100:
        return 0.9
    if rp < 200:
        return 0.85
    if rp < 400:
        return 0.8


# 初始登录界面
@app.route('/')
def startup():
    if len(customer) == 0:
        return render_template('login.html')
    else:
        return render_template('index.html', customer = customer)

# 首页
@app.route('/index')
def index():
    global customer
    print(customer)
    if len(customer) == 0:
        return render_template('login.html')
    else:
        return render_template('index.html', customer = customer)


# 注册
@app.route('/register', methods=['GET','POST'])
def register():
    global customer
    if request.method == 'POST':
        usr_name = request.form['usr-name']
        pw1 = request.form['pw1']
        pw2 = request.form['pw2']
        sql = "SELECT * FROM customer WHERE CustomerName = '"+usr_name+"';"  
        cur = con.cursor()
        cur.execute(sql)
        tmp = cur.fetchall()
        if len(tmp) != 0:
            flash('用户名已存在，请重新选择')
        elif pw1 != pw2:
            flash('密码不一致，请重新输入')
        elif 6 > len(pw1) or len(pw1) > 15:
            flash('密码需由6~15个字符组成，请重新输入')
        elif pw1 == pw2 and 6 <= len(pw1) <= 15:
            cur = con.cursor()
            cur.execute("INSERT INTO customer(CustomerName, Password, RedemptionPoints) VALUES(%s, %s, 0)", (usr_name,hashlib.md5(pw1.encode("utf-8")).hexdigest()))
            con.commit()
            customer = usr_name
            return render_template('index.html', customer = usr_name)
    return render_template('register.html')


# 登出
@app.route('/logout', methods=['GET','POST'])
def logout():
    global customer
    logger.info("用户"+customer+"登出")
    customer = ""
    return render_template('login.html')


# 登录
@app.route('/login', methods=['GET','POST'])
def login():
    global customer
    if request.method == 'POST':
        usr_name = request.form['usr-name']
        pw1 = request.form['pw1'].encode("utf-8")
        sql_query = "SELECT Password FROM customer WHERE CustomerName = '"+usr_name+"';"  
        tmp = select(sql_query)
        if len(tmp) == 0:
            print('输入用户名和密码错误')
            flash('用户名和密码错误，请重试')
            return render_template('login.html')
        tmp_pw = tmp[0][0]
        if tmp_pw == hashlib.md5(pw1).hexdigest():
            print('登录成功')
            customer = usr_name
            return render_template('index.html', customer = customer)
        else:
            logger.info('用户名和密码错误')
            flash('用户名和密码错误，请重试')
            return render_template('login.html')
    else:
        return render_template('login.html')


# sql查询
@app.route('/search_book/<argv>', methods=['GET','POST'])
def search_book(argv):
    global customer
    search_case=""
    query_txt=""
    if argv == 'cart':
        if request.method == 'POST':
            sql_query = "SELECT max(OrderID) FROM `order`"
            OrderID = select(sql_query)[0][0]+1
            print(OrderID)
            sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
            CustomerID = select(sql_query)[0][0]
            today=datetime.date.today()
            sql_query = "INSERT IGNORE INTO `order` VALUES ('"+str(OrderID)+"', '"+str(CustomerID)+"', '"+str(today)+"','in cart', NULL, NULL)"
            insert(sql_query)
            ISBN = session['ISBN']
            quantity = request.form['quantity']
            branch = request.form['branch']
            sql_query = "INSERT INTO `order_entry` VALUES ('"+str(OrderID)+"', '"+str(ISBN)+"', '"+str(branch)+"', '"+str(quantity)+"', 1.0)"
            insert(sql_query)
            return redirect(url_for('search_book', argv = 'search'))

    if argv == 'search':
        if request.method == 'POST':
            search_case = request.form['search_case']
            query_txt = request.form['query_txt']
            session['search_case'] = search_case
            session['query_txt'] = query_txt
        SelectFrom='''SELECT book.ISBN,book.Title,group_concat(DISTINCT compose.AuthorName) AS AuthorName,
        book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro FROM book,compose '''
        checked='checked="checked"'
        if query_txt == "":
            query_txt = session['query_txt']
        if search_case == "":
            search_case = session['search_case']
        if search_case == 'book_name':
            sql_query = SelectFrom+"WHERE (book.Title) LIKE '%"+query_txt+"%'" \
                        "AND compose.ISBN = book.ISBN " \
                        "GROUP BY book.ISBN;"
            data = littleselect(sql_query)
            session['sql_query'] = sql_query
            return render_template('query.html', book=checked, query_txt=query_txt, data = data, customer = customer)
        elif search_case == 'author':
            sql_query = SelectFrom+"WHERE book.ISBN = compose.ISBN AND book.ISBN = compose.ISBN AND (compose.AuthorName) LIKE '%"+query_txt+"%' GROUP BY book.ISBN;"
            data = littleselect(sql_query)
            session['sql_query'] = sql_query
            return render_template('query.html', author=checked, query_txt=query_txt, data = data, customer = customer)
        elif search_case == 'ch_book_info':
            sql_query = SelectFrom+"WHERE ((book.ChineseIntro) LIKE '%"+query_txt+"%') AND compose.ISBN = book.ISBN GROUP BY book.ISBN;"
            data = littleselect(sql_query)
            session['sql_query'] = sql_query
            return render_template('query.html', ch_info=checked, query_txt=query_txt, data = data, customer = customer)
        elif search_case == 'stock':
            sql_query = "SELECT book.Title,SUM(stock.Quantity) AS TotalStock FROM book LEFT JOIN stock ON book.ISBN = stock.ISBN WHERE (book.Title) LIKE '%"+query_txt+"%'GROUP BY Title;"
            data = select(sql_query)
            html_str = ""
            for record in data:
                html_str += '<table> <div class="mytable">'
                html_str += f'<tr><th>书名:</th><td>{record[0]}</td></tr>'
                html_str += f'<tr><th>总库存:</th><td>{record[1]}</td></tr>'
                html_str += "</table>"
            return render_template('query.html', stock=checked, query_txt=query_txt, content=html_str, customer = customer)
    if 'sql_query' in session:
        return render_template('query.html', data = select(session['sql_query']), customer = customer)
    return render_template('query.html', customer = customer)


# 图书主页
@app.route('/book/<argv>', methods=['GET','POST'])
def book(argv):
    print(request.url)
    session['ISBN'] = argv
    sql_query="SELECT book.ISBN,book.Title,group_concat(DISTINCT compose.AuthorName) AS AuthorName,"\
    "book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro FROM book,compose WHERE book.ISBN LIKE "+\
    argv+" AND compose.ISBN = book.ISBN GROUP BY book.ISBN;"
    return render_template('bookinfo.html', data = select(sql_query)[0], customer=customer)


# 客户信息显示
@app.route('/customer/<argv>', methods=['GET','POST'])
def Customer(argv):
    global customer
    if argv == "default":
        return render_template('customer.html', customer = customer)
    elif argv == "cart":
        sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
        CustomerID = select(sql_query)[0][0]
        sql_query = "SELECT order_entry.*,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID WHERE order.Status = 'in cart' AND order.CustomerID = " + str(CustomerID) + " ;"
        data = select(sql_query)
        html_str = '<form action="/customer/cart" method="POST">'
        for record in data:
            html_str += '<table> <div class="mytable">'
            html_str += f'<tr><th><input type="checkbox" name="chkbox" value="{record[0]}">订单号:</th><td>{record[0]}</td></tr>'
            html_str += f'<tr><th>ISBN:</th><td>{record[1]}</td></tr>'
            html_str += f'<tr><th>门店:</th><td>{record[2]}</td></tr>'
            html_str += f'<tr><th>数量:</th><td>{record[3]}</td></tr>'
            html_str += '</div></table>'
        html_str += '<input type="submit" value="下单"></form>'
        if request.method == 'POST':
            chkbox_values = request.form.getlist('chkbox')
            if len(chkbox_values) != 0:
                sql_query = "SELECT max(OrderID) FROM `order`"
                OrderID = select(sql_query)[0][0]+1
                print(OrderID)
                today = datetime.date.today()
                sql_query = "INSERT IGNORE INTO `order` VALUES ('"+str(OrderID)+"', '"+str(CustomerID)+"', '"+str(today)+"','undone', NULL, NULL)"
                insert(sql_query)
                for chkbox_value in chkbox_values:
                    sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
                    CustomerID = select(sql_query)[0][0]   
                    sql_query = "SELECT RedemptionPoints FROM customer WHERE CustomerName='"+customer+"';"
                    RedemptionPoints = int(select(sql_query)[0][0])
                    Discount = rp2dis(RedemptionPoints)
                    sql_query = "UPDATE `order_entry` SET Discount = "+ str(Discount) +", OrderID = " + str(OrderID) + " WHERE OrderID = '" + chkbox_value + "';"
                    insert(sql_query)
                    sql_query = "DELETE FROM `order` WHERE OrderID = " + chkbox_value + ";"
                    insert(sql_query)
            return redirect(url_for('Customer', argv = 'cart'))
        return render_template('customer.html', content = html_str, customer = customer)
    elif argv == "info":
        sql_query = "SELECT * FROM customer WHERE CustomerName='"+customer+"';"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table> <div class="mytable">'
            html_str += f'<tr><th>ID:</th><th>用户名:</th><th>积分:</th></tr>'
            html_str += f'<tr><td>{record[0]}</td><td>{record[1]}</td><td>{record[3]}</td></tr>'
            html_str += '</div></table>'
        return render_template('customer.html', content = html_str, customer = customer)
    elif argv == "history":
        sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
        CustomerID = select(sql_query)[0][0]
        sql_query = "SELECT * FROM `order` WHERE order.Status != 'in cart' AND order.CustomerID = " + str(CustomerID) + ";"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table> <div class="mytable">'
            html_str += f'<tr><th>订单号:</th><td><a href="/historyorder/{record[0]}" target="_parent">{record[0]}</a></td></tr>'
            html_str += f'<tr><th>日期:</th><td>{record[2]}</td></tr>'
            html_str += f'<tr><th>留言:</th><td>{record[4]}</td></tr>'
            html_str += f'<tr><th>回复:</th><td>{record[5]}</td></tr>'
            html_str += f'<tr><th>状态:</th><td>{record[3]}</td></tr>'
            html_str += '</div></table>'
        return render_template('customer.html', content = html_str, customer = customer)
    elif argv == "changepw":
        html_str = '<form class="top-info" action="/customer/changepw" method="POST">'
        html_str += f'<div class="input-wrap"><input class="input-txt" type="password" name="newpw1" placeholder="请输入原密码"></div>'
        html_str += f'<div class="input-wrap"><input class="input-txt" type="password" name="newpw2" placeholder="请输入新密码"></div>'
        html_str += f'<input type="submit" value="修改密码">'
        html_str += f'</form>'
        if request.method == 'POST':
            pw1 = request.form['newpw1']
            pw2 = request.form['newpw2']
            sql = "SELECT * FROM customer WHERE CustomerName = '"+customer+"';"  
            tmp = select(sql)
            if len(tmp) == 0:
                print('用户名不存在')
            elif pw1 != pw2:
                print('密码不一致，请重新输入')
            elif 6 > len(pw1) or len(pw1) > 15:
                print('密码需由6~15个字符组成，请重新输入')
            else:
                print('密码修改成功')
                cur = con.cursor()
                cur.execute("UPDATE customer SET Password = '" + hashlib.md5(pw1.encode("utf-8")).hexdigest() + "' WHERE CustomerName = '" + customer + "';")
                con.commit()
                return render_template('customer.html', content = html_str, customer = customer)
        return render_template('customer.html', content = html_str, customer = customer)
    elif argv == "message":
        sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
        CustomerID = select(sql_query)[0][0]
        sql_query = "SELECT * FROM `order` WHERE order.CustomerID = " + str(CustomerID) + ";"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table> <div class="mytable">'
            html_str += f'<tr><th>订单号:</th><td><a href="/messageorder/{record[0]}" target="_parent">{record[0]}</a></td></tr>'
            html_str += f'<tr><th>日期:</th><td>{record[2]}</td></tr>'
            html_str += f'<tr><th>留言:</th><td>{record[4]}</td></tr>'
            html_str += f'<tr><th>回复:</th><td>{record[5]}</td></tr>'
            html_str += f'<tr><th>状态:</th><td>{record[3]}</td></tr>'
            html_str += '</div></table>'
        if request.method == 'POST':
            message = request.form['message']
            sql_query = "UPDATE `order` SET Message = '" + message + "' WHERE OrderID = '" + session['MesOrderID'] + "';"
            insert(sql_query)
            return redirect(url_for('Customer', argv = 'message'))
        return render_template('customer.html', content = html_str, customer = customer)
    else:
        return render_template('customer.html', customer = customer)


@app.route('/messageorder/<argv>', methods = ['GET','POST'])
def messageorder(argv):
    sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
    CustomerID = select(sql_query)[0][0]
    sql_query = "SELECT order_entry.*,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID WHERE order.CustomerID = " + str(CustomerID) + " AND order.OrderID = " + argv + " ;"
    data = select(sql_query)
    html_str = '<form action="/customer/message" method="POST">'
    for record in data:
        html_str += '<table> <div class="mytable">'
        html_str += f'<tr><th>订单号:</th><td>{record[0]}</td></tr>'
        html_str += f'<tr><th>ISBN:</th><td>{record[1]}</td></tr>'
        html_str += f'<tr><th>门店:</th><td>{record[2]}</td></tr>'
        html_str += f'<tr><th>数量:</th><td>{record[3]}</td></tr>'
        html_str += f'<tr><th>折扣:</th><td>{record[4]}</td></tr>'
        html_str += f'<tr><th>日期:</th><td>{record[5]}</td></tr>'
        html_str += f'<tr><th>留言:</th><td>{record[6]}</td></tr>'
        html_str += f'<tr><th>回复:</th><td>{record[7]}</td></tr>'
        html_str += f'<tr><th>状态:</th><td>{record[8]}</td></tr>'
        html_str += '</div></table>'
    html_str += '<input class="input-txt" name="message" type="text" placeholder="新留言">'
    html_str += '<input type="submit" value="修改"></form>'
    session['MesOrderID'] = argv
    return render_template('customer.html', content = html_str, customer = customer)


@app.route('/historyorder/<argv>', methods = ['GET','POST'])
def historyorder(argv):
    sql_query = "SELECT CustomerID FROM customer WHERE CustomerName='"+customer+"';"
    CustomerID = select(sql_query)[0][0]
    sql_query = "SELECT order_entry.*,order.Date,order.Message,order.Reply,order.Status FROM order_entry INNER JOIN `order` ON order.OrderID = order_entry.OrderID WHERE order.CustomerID = " + str(CustomerID) + " AND order.OrderID = " + argv + " ;"
    data = select(sql_query)
    html_str = ""
    for record in data:
        html_str += '<table> <div class="mytable">'
        html_str += f'<tr><th>订单号:</th><td>{record[0]}</td></tr>'
        html_str += f'<tr><th>ISBN:</th><td>{record[1]}</td></tr>'
        html_str += f'<tr><th>门店:</th><td>{record[2]}</td></tr>'
        html_str += f'<tr><th>数量:</th><td>{record[3]}</td></tr>'
        html_str += f'<tr><th>折扣:</th><td>{record[4]}</td></tr>'
        html_str += f'<tr><th>日期:</th><td>{record[5]}</td></tr>'
        html_str += f'<tr><th>留言:</th><td>{record[6]}</td></tr>'
        html_str += f'<tr><th>回复:</th><td>{record[7]}</td></tr>'
        html_str += f'<tr><th>状态:</th><td>{record[8]}</td></tr>'
        html_str += '</div></table>'
    return render_template('customer.html', content = html_str, customer = customer)


if __name__ == "__main__":
    logger = logg.get_logger(__name__)
    logg.dump_MySQL(True)
    app.run(debug=True)
