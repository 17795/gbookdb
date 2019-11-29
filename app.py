from flask import Flask, render_template, request
from pymysql import *

con = connect("localhost", "root", "", "gbookdb")

app = Flask(__name__, static_url_path='')


# sql查询
def select(sql_query):
    cur = con.cursor()
    print("OK")
    cur.execute(sql_query)
    print("OK2")
    data = cur.fetchall()
    print(data)
    return data


# 从查询结果生成html文本
def output_html(data): # 显示查询结果的web页面
    html_str = ""
    for record in data:
        # 改了好长时间…在default.css文件里重新定义了表格格式（删除了query里的table格式），但是运行结果一直没有改变
        # ！！！！！！！！！！！看这里啊
        # ——: 上面的，我页脚的背景颜色哪儿去了？你改default别动我footer啊，页脚没背景看不清啊
        html_str += '<table> <div class="mytable">'
        html_str += f'<tr><th>ISBN:</th><td>{record[0]}</td></tr>'
        html_str += f'<tr><th>书名:</th><td>{record[1]}</td></tr>'
        html_str += f'<tr><th>作者:</th><td>{record[2]}</td></tr>'
        html_str += f'<tr><th>出版社:</th><td>{record[3]}</td></tr>'
        html_str += f'<tr><th>售价:</th><td>{record[4]}</td></tr>'
        html_str += f'<tr><th>简介:</th><td>{record[5]}</td></tr>'
        html_str += f'<tr><th>Introduction:</th><td>{record[6]}</td></tr>'
        html_str += "</div></table>"
    return html_str


checked='checked="checked"'


# 默认搜索界面
@app.route('/')
def index():
    return app.send_static_file("index.html")


# sql查询
@app.route('/search_book', methods=['POST'])
def search_book():
    search_case = request.form['search_case']
    query_txt = request.form['query_txt']
    if search_case == 'book_name':
        sql_query = "SELECT book_info.ISBN,book_info.BookName,group_concat(DISTINCT author.Writer) AS Writer," \
                    "book_info.Publisher,book_info.Price,book_info.ChineseIntro,book_info.EnglishIntro " \
                    "FROM book_info,author WHERE (book_info.BookName) LIKE '%"+query_txt+"%'" \
                    "AND author.ISBN = book_info.ISBN " \
                    "GROUP BY book_info.ISBN;"
        data = select(sql_query)
        return render_template('query.html', book=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'author':
        sql_query = "SELECT book_info.ISBN,book_info.BookName,group_concat(DISTINCT author.Writer) AS Writer," \
                    "book_info.Publisher,book_info.Price,book_info.ChineseIntro,book_info.EnglishIntro " \
                    "FROM book_info,author WHERE book_info.ISBN = author.ISBN AND book_info.ISBN =(SELECT ISBN" \
                    " FROM author WHERE (author.Writer) LIKE '%"+query_txt+"%') GROUP BY book_info.ISBN;"
        data = select(sql_query)
        return render_template('query.html', author=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'ch_book_info':
        sql_query = "SELECT book_info.ISBN,book_info.BookName,group_concat(DISTINCT author.Writer) AS Writer," \
                    "book_info.Publisher,book_info.Price,book_info.ChineseIntro,book_info.EnglishIntro " \
                    "FROM book_info,author WHERE ((book_info.ChineseIntro) LIKE '%"+query_txt+"%')" \
                    "AND author.ISBN = book_info.ISBN GROUP BY book_info.ISBN;"
        data = select(sql_query)
        return render_template('query.html', ch_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'en_book_info':
        sql_query = "SELECT book_info.ISBN,book_info.BookName,group_concat(DISTINCT author.Writer) AS Writer," \
                    "book_info.Publisher,book_info.Price,book_info.ChineseIntro,book_info.EnglishIntro " \
                    "FROM book_info,author WHERE ((book_info.EnglishIntro) LIKE '%"+query_txt+"%')" \
                    "AND author.ISBN = book_info.ISBN GROUP BY book_info.ISBN;"
        data = select(sql_query)
        return render_template('query.html', en_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'stock':
        sql_query = "SELECT book_info.BookName,SUM(stock.Stock) AS 总库存 " \
                    "FROM book_info INNER JOIN stock ON book_info.ISBN = stock.ISBN WHERE (book_info.BookName) " +\
                    "LIKE '%"+query_txt+"%'GROUP BY BookName;"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table border="1">'
            html_str += f'<tr><th>书名:</th><td>{record[0]}</td></tr>'
            html_str += f'<tr><th>总库存:</th><td>{record[1]}</td></tr>'
            html_str += "</table><br/>"
        return render_template('query.html', stock=checked, query_txt=query_txt, content=html_str)
    elif search_case == 'order':
        sql_query = "SELECT order.ID AS OrderID,book_info.BookName,order.Branch,stock.Stock,order.Size " \
                    "FROM stock INNER JOIN book_info ON (book_info.ISBN = stock.ISBN)INNER JOIN `order` " \
                    "ON (order.ISBN = book_info.ISBN)AND (stock.Branch = order.Branch)AND (stock.ISBN = order.ISBN)" \
                    "WHERE order.ID = "+query_txt+";"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table border="1">'
            html_str += f'<tr><th>订单号</th><th>书名</th><th>门店编号</th><th>出货量</th><th>顾客编号</th></tr>'
            html_str += f'<tr><td>{record[0]}</td><td>{record[1]}</td><td>{record[2]}</td><td>{record[3]}</td><td>{record[4]}</td></tr>'
            html_str += "</table><br/>"
        return render_template('query.html', order=checked, query_txt=query_txt, content=html_str)
    #elif search_case == 'user':
        # 或者把顾客查询写这里？
        #return render_template('user.html', query_txt=query_txt, content=s)


@app.route('/user', methods=['POST'])
def user():
    # 在这里实现user的查询，权限是用户自身
    s=""
    return render_template('user.html', content=s)
    
    
def insert(sql_query):
    cur = con.cursor()
    print("OK3")
    cur.execute(sql_query)
    print("OK4")


# 注册功能
@app.route('/')
def register():
    usr_name = request.form['usr-name']
    pw1 = request.form['pw1']
    pw2 = request.form['pw2']
    if pw1==pw2 and len(pw1)<=15:
        sql_query = "INSERT INTO vip_info (`customer_name`,`discount`,`password`) VALUES(" + usr_name+",1.00," + pw1 +");"
        insert(sql_query)
    

if __name__ == "__main__":
    app.run(debug=True)
