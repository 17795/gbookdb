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
    print(data)
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
        sql_query = "SELECT book.ISBN,book.BookName,group_concat(DISTINCT author.Author) AS Author," \
                    "book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro " \
                    "FROM book,author WHERE (book.BookName) LIKE '%"+query_txt+"%'" \
                    "AND author.ISBN = book.ISBN " \
                    "GROUP BY book.ISBN;"
        data = select(sql_query)
        return render_template('query.html', book=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'author':
        sql_query = "SELECT book.ISBN,book.BookName,group_concat(DISTINCT author.Author) AS Author," \
                    "book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro " \
                    "FROM book,author WHERE book.ISBN = author.ISBN AND book.ISBN =(SELECT ISBN" \
                    " FROM author WHERE (author.Author) LIKE '%"+query_txt+"%') GROUP BY book.ISBN;"
        data = select(sql_query)
        return render_template('query.html', author=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'ch_book':
        sql_query = "SELECT book.ISBN,book.BookName,group_concat(DISTINCT author.Author) AS Author," \
                    "book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro " \
                    "FROM book,author WHERE ((book.ChineseIntro) LIKE '%"+query_txt+"%')" \
                    "AND author.ISBN = book.ISBN GROUP BY book.ISBN;"
        data = select(sql_query)
        return render_template('query.html', ch_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'en_book':
        sql_query = "SELECT book.ISBN,book.BookName,group_concat(DISTINCT author.Author) AS Author," \
                    "book.Publisher,book.Price,book.ChineseIntro,book.EnglishIntro " \
                    "FROM book,author WHERE ((book.EnglishIntro) LIKE '%"+query_txt+"%')" \
                    "AND author.ISBN = book.ISBN GROUP BY book.ISBN;"
        data = select(sql_query)
        return render_template('query.html', en_info=checked, query_txt=query_txt, content=output_html(data))
    elif search_case == 'stock':
        sql_query = "SELECT book.BookName,SUM(stock.Stock) AS TotalStock " \
                    "FROM book INNER JOIN stock ON book.ISBN = stock.ISBN WHERE (book.BookName) " +\
                    "LIKE '%"+query_txt+"%'GROUP BY BookName;"
        data = select(sql_query)
        html_str = ""
        for record in data:
            html_str += '<table><div class="mytable">'
            html_str += f'<tr><th>书名:</th><td>{record[0]}</td></tr>'
            html_str += f'<tr><th>总库存:</th><td>{record[1]}</td></tr>'
            html_str += "</div></table>"
        return render_template('query.html', stock=checked, query_txt=query_txt, content=html_str)
    
    
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
        sql_query = "INSERT INTO customer(`CustomerName`,`Discount`,`Password`) VALUES(" + usr_name+",1.00," + pw1 +");"
        insert(sql_query)
    

if __name__ == "__main__":
    app.run(debug=True)
