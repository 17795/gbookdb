import os
import logging
import time

import sys

LOG_PATH = 'logs'
LOG_FILE = 'log.txt'
SQL_PATH = 'backup/'


def get_logger(name):
    logger = logging.getLogger(name)
    if not os.path.exists(LOG_PATH):
        os.mkdir(LOG_PATH)
    formatter = logging.Formatter('%(asctime)s %(levelname)-8s: %(message)s')
    # 文件
    file_handler = logging.FileHandler("%s/%s" % (LOG_PATH, LOG_FILE))
    file_handler.setFormatter(formatter)
    # 控制台
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.formatter = formatter
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    # 最低输出级别
    logger.setLevel(logging.INFO)
    return logger

# 使用示例：
# logger.info('用户%s登出' % customer)
# logger.debug('管理员%s 登录')
# logger.warning('管理员%s修改' % sql_query)
# logger.error('用户查询%s失败' % sql_query)


# 数据库名称固定为gbookdb
# 参数分别表示数据库root的密码、是否生成对应数据库
def dump_MySQL(password,toDump):
    if toDump:
        if not os.path.exists('backup'):
            os.mkdir('backup')
        dbname = 'gbookdb'
        sqlname = str(time.strftime("%H-%M-%S", time.localtime())) + '.sql'
        sql = 'mysqldump -uroot -p' + password +' '+ dbname + '>' + SQL_PATH + sqlname
        os.system(sql)


