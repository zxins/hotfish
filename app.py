# -*- coding: utf-8 -*-
import json
from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from flask_caching import Cache

app = Flask(__name__)
app.config.from_pyfile('config.py')

db = SQLAlchemy(app)

# 缓存
cache = Cache(app,  config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 10})

@app.route('/')
@cache.cached()
def index():
    sql = "select `data`, `data_type`, `name`, `created` from hotrows " \
          "where id in (select max(id) from hotrows group by data_type)"
    rows = db.engine.execute(sql)
    results = []
    for row in rows:
        results.append({
            'data': json.loads(row.data),
            'data_type': row.data_type,
            'name': row.name,
            'created': row.created.strftime("%Y-%m-%d %H:%M:%S")
        })
    return render_template('index.html', results=results)


@app.route('/api')
@cache.cached()
def index_api():
    rows = db.engine.execute("select * from hotrows")
    results = []
    for row in rows:
        results.append({
            'data': json.loads(row.data),
            'data_type': row.data_type,
            'name': row.name,
            'created': row.created.strftime("%Y-%m-%d %H:%M:%S")
        })
    return jsonify(results)


if __name__ == '__main__':
    app.run()
