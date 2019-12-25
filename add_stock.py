# import json
from flask import Flask, render_template, request
from pymysql import *
import logg

con = connect("localhost", "root", "", "gbookdb")

app = Flask(__name__, static_url_path='')


# sql查询
def select(sql_query):
    #logger.info(sql_query)
    cur = con.cursor()
    cur.execute(sql_query)
    print("SELECT FROM gbookdb OK")
    data = cur.fetchall()
    # print(data)
    return data


def insert(sql_query):
    #logger.info(sql_query)
    cur = con.cursor()
    cur.execute(sql_query)
    con.commit()
    print("INSERT INTO gbookdb OK")


sql_query = "SELECT ISBN FROM book"
book_ISBN = list(select(sql_query))
print(book_ISBN)
for ISBN in book_ISBN:
    for Branch in range(1, 4):
        sql_query = "INSERT INTO stock (`ISBN`,`BranchID`,`Quantity`) VALUES('"+ISBN[0]+"','"+str(Branch)+"',100);"
        insert(sql_query)


if __name__ == "__main__":
    #logger = logg.get_logger(__name__)
    #logg.dump_MySQL(True)
    app.run(debug=True)
