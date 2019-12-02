# gbookdb
 - 基于MySQL的书店数据库系统
 - 基于Flask的后端程序
 - 基于easyUI的前端网页设计

## 数据库结构更新
于2019-12-2约17:00的提交中更新了数据库结构（见commit message），因此与数据库结构有关的后端代码几乎都需要更改。截止至本次提交，更改均**未完成**，目前后端程序在很大程度上处于**不可用状态**。

### 已完成的功能
面向客户的部分：

 - ~~图书信息的相关查询实现~~
 - 用户注册的函数
 - 登录、查询、书店主页的页面设计完成

面向管理人员的部分：

 - 网页设计完成
 - ~~对各个表格的添加、删除、修改、查询、通过SQL语句查询功能均已实现~~
 - 表格中长文本的显示方式优化
 - 修改时对空信息默认不更改

### 待完成的功能

面向客户的部分：
 - 登录、注册页面和后端程序的对接
 - 根据登录状态不同修改查询功能的权限
 - 购物车/订单功能

面向管理人员的部分：

 - ```searchEntry```功能是否需要完善
 - 多后台并行时数据库业务的一致性和原子性完善
 - 界面美化

其他部分：

 - 选择并实现扩展功能
 - 如果可能的话，部署到服务器
 - 爬取作者简介字段（或者删除该字段，目前全部为null）

### GitHub操作相关
[Git配置](https://git-scm.com/book/zh/v2/%E8%B5%B7%E6%AD%A5-%E5%88%9D%E6%AC%A1%E8%BF%90%E8%A1%8C-Git-%E5%89%8D%E7%9A%84%E9%85%8D%E7%BD%AE)

[Git生成SSH公钥](https://git-scm.com/book/zh/v2/%E6%9C%8D%E5%8A%A1%E5%99%A8%E4%B8%8A%E7%9A%84-Git-%E7%94%9F%E6%88%90-SSH-%E5%85%AC%E9%92%A5)

[GitHub的SSH配置](https://help.github.com/cn/github/authenticating-to-github/connecting-to-github-with-ssh)

[GitHub多人合作](https://www.cnblogs.com/schaepher/p/4933873.html)

[GitHub中文帮助文档](https://help.github.com/cn)
