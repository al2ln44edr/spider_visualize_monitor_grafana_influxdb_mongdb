import ast
import time
import pymongo
import traceback
from configparser import ConfigParser
from influxdb import InfluxDBClient
from datetime import datetime
from os.path import getmtime

# 配置 influxdb
client = InfluxDBClient(host='localhost', port=8086) # influxdb默认端口为8086

# 创建 database
client.create_database('Spider')
# switch 到 database
client.switch_database('Spider')

# 设定配置文件
config_name = 'influx_settings.conf'

WATCHED_FILES = [config_name]
WATCHED_FILES_MTIMES = [(f, getmtime(f)) for f in WATCHED_FILES]  

_count_dict = {}
_size_dict = {}

# 获取配置文件中的设置
def parse_config(file_name):

    try:
        # 创建一个配置文件对象
        cf = ConfigParser() 
 
        # 打开配置文件
        cf.read(file_name)

        # 获取配置文件中的统计频率
        interval = cf.getint('time', 'interval')
        
        # 获取配置文件中要监控的 dbs 和 collection
        dbs_and_collections = ast.literal_eval(cf.get('db', 'db_collection_dict'))
        
        return interval, dbs_and_collections

    except:
        print(traceback.print_exc())
        return None


# 从 MongoDB 获取数据，并写入 InfluxDB
def insert_data(dbs_and_collections):

    # 连接 MongoDB 数据库
    mongodb_client = pymongo.MongoClient(host='127.0.0.1',port=27017)  # 直接使用默认地址端口连接 MongoDB

    for db_name, collection_name in dbs_and_collections.items():
        
        # 数据库操作，创建 collection 集合对象
        db = mongodb_client[db_name]
        collection = db[collection_name]
        
        # 获取 collection 集合大小
        collection_size = round(float(db.command("collstats", collection_name).get('size')) / 1024 / 1024, 2)
        
        # 获取 collection 集合内数据条数
        current_count = collection.count()

        # 初始化数据条数，当程序刚执行时，条数初始量就设置为第一次执行时获取的数据
        init_count = _count_dict.get(collection_name, current_count)
        # 初始化数据大小，当程序刚执行时，大小初始量就设置为第一次执行时获取的数据大小
        init_size = _size_dict.get(collection_name, collection_size)

        # 得到数据条数增长量
        increase_amount = current_count - init_count        
        # 得到数据大小增长量
        increase_collection_size = collection_size - init_size

        # 得到当前时间
        current_time = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')

        # 赋值
        _count_dict[collection_name] = current_count
        _size_dict[collection_name] = collection_size

        # 构建
        json_body = [
            {
                "measurement": "crawler",
                "time": current_time,
                "tags": {
                    "spider_name": collection_name
                },
                "fields": {
                    "count": current_count,
                    "increase_count": increase_amount,
                    "size": collection_size,
                    "increase_size": increase_collection_size

                }
            }
        ]
        # 将获取
        if client.write_points(json_body):
            print('成功写入influxdb！',json_body)


def main():
    # 获取配置文件中的监控频率和MongoDB数据库设置
    interval, dbs_and_collexctions = parse_config(config_name)

    # 如果配置有问题则报错
    if (interval or dbs_and_collexctions) is None:
        raise ValueError('配置有问题，请打开配置文件重新设置！')

    print('设置监控频率：', interval)
    print('设置要监控的MongoDB数据库和集合：', dbs_and_collexctions)

    last_interval = interval
    last_dbs_and_collexctions = dbs_and_collexctions

    # 这里实现配置文件热更新
    for f, mtime in WATCHED_FILES_MTIMES:
        while True:
            # 检查配置更新情况，如果文件有被修改，则重新获取配置内容
            if getmtime(f) != mtime:
                # 获取配置信息
                interval, dbs_and_collections = parse_config(config_name)
                print('提示：配置文件于 %s 更新！' % (time.strftime("%Y-%m-%d %H:%M:%S")))
                
                # 如果配置有问题，则使用上一次的配置
                if (interval or dbs_and_collexctions) is None:
                    interval = last_interval
                    dbs_and_collexctions = last_dbs_and_collexctions

                else:
                    print('使用新配置！')
                    print('新配置内容:', interval, dbs_and_collexctions)
                    mtime = getmtime(f)

            # 写入 influxdb 数据库
            insert_data(dbs_and_collexctions)

            # 使用 sleep 设置每次写入的时间间隔
            time.sleep(interval)

if __name__ == '__main__':
    main()
