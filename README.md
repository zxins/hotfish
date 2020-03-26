#### 获取各大热门网站热门头条的多线程爬虫，使用Flask聚合网站  

知乎、V2EX、微博、贴吧、IT之家、豆瓣、虎扑、天涯、GitHub等网站排行榜

![](https://tva1.sinaimg.cn/large/00831rSTly1gd7cq5klbxj30zk0k2414.jpg)

#### 使用步骤：
数据库表结构见`hotrows.sql`  
先修改`spiders.py` 和 `config.py` 的数据库配置

1. 安装依赖
```shell script
pip install -r requirements.txt
```  

2. 运行爬虫(建议设为定时任务)
```shell script
python spiders.py
```

3. 启动Flask
```shell script
python app.py
```