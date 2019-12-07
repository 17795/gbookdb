from flask import Flask, render_template, request
from pymysql import *

con = connect("localhost", "root", "", "gbookdb")
app = Flask(__name__, static_url_path='')

# 封装 sql 操作
def select(sql_query):
    cur = con.cursor()
    cur.execute(sql_query)
    data = cur.fetchall()
    return data

# 从查询结果生成html文本
def output_html(data): # 显示查询结果的web页面
    html_str = ""
    for record in data:
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


# 默认搜索界面
@app.route('/')
def index():
    return app.send_static_file("index.html")


# sql查询
@app.route('/search_book', methods=['POST'])
def search_book():
    search_case=request.form['search_case']
    query_txt=request.form['query_txt']
    SelectFrom='''SELECT book.ISBN,book.BookName,group_concat(DISTINCT author.Author) AS Author,
    book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro FROM book,author '''
    checked='checked="checked"'

    if search_case == 'book_name':
        sql_query = SelectFrom+"WHERE (book.BookName) LIKE '%"+query_txt+"%'" \
                    "AND author.ISBN = book.ISBN " \
                    "GROUP BY book.ISBN;"
        data = select(sql_query)
        return render_template('query.html', book=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'author':
        sql_query = SelectFrom+'''WHERE book.ISBN = author.ISBN AND book.ISBN =(
            SELECT ISBN FROM author WHERE (author.Author) LIKE '%"+query_txt+"%') GROUP BY book.ISBN;'''
        data = select(sql_query)
        return render_template('query.html', author=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'ch_book_info':
        sql_query = SelectFrom+'''WHERE ((book.ChineseIntro) LIKE '%"+query_txt+"%') 
            AND author.ISBN = book.ISBN GROUP BY book.ISBN;'''
        data = select(sql_query)
        return render_template('query.html', ch_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'en_book_info':
        sql_query = SelectFrom+'''WHERE ((book.EnglishIntro) LIKE '%"+query_txt+"%') 
            AND author.ISBN = book.ISBN GROUP BY book.ISBN;'''
        data = select(sql_query)
        return render_template('query.html', en_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'stock':
        sql_query = '''SELECT book.BookName,SUM(stock.Stock) AS 总库存 
            FROM book INNER JOIN stock ON book.ISBN = stock.ISBN 
            WHERE (book.BookName) LIKE '%"+query_txt+"%'GROUP BY BookName;'''
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table border="1">'
            html_str += f'<tr><th>书名:</th><td>{record[0]}</td></tr>'
            html_str += f'<tr><th>总库存:</th><td>{record[1]}</td></tr>'
            html_str += "</table><br/>"
        return render_template('query.html', stock=checked, query_txt=query_txt, content=html_str)
    elif search_case == 'order':
        sql_query = "SELECT order.ID AS OrderID,book.BookName,order.Branch,stock.Stock,order.Size " \
                    "FROM stock INNER JOIN book ON (book.ISBN = stock.ISBN)INNER JOIN `order` " \
                    "ON (order.ISBN = book.ISBN)AND (stock.Branch = order.Branch)AND (stock.ISBN = order.ISBN)" \
                    "WHERE order.ID = "+query_txt+";"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table border="1">'
            html_str += f'<tr><th>订单号</th><th>书名</th><th>门店编号</th><th>出货量</th><th>顾客编号</th></tr>'
            html_str += f'<tr><td>{record[0]}</td><td>{record[1]}</td><td>{record[2]}</td><td>{record[3]}</td><td>{record[4]}</td></tr>'
            html_str += "</table><br/>"
        return render_template('query.html', order=checked, query_txt=query_txt, content=html_str)

def insert(usr_name,pw):
    cur = con.cursor()
    cur.execute("INSERT INTO customer(CustomerName, Password, RedemptionPoints) VALUES(%s, %s, 0)", (usr_name,pw))


# 注册功能
@app.route('/regist', methods=['POST'])
def register():
    usr_name = request.form['usr-name']
    pw1 = request.form['pw1']
    pw2 = request.form['pw2']
    # print(usr_name)
    # print(pw1)
    ch='\"'
    if pw1==pw2 and len(pw1)<=15:
        insert(usr_name,pw1)
    return render_template('query.html')
    

if __name__ == "__main__":
    app.run(debug=True)
