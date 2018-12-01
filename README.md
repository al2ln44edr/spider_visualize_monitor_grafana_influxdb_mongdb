# spider_visualize_monitor


1.前言

本文介绍的方法，是使用 Grafana 和 InfluxDB 对爬虫进行可视化监控。

配置过程详情，请参考：https://www.jianshu.com/p/9de223e05a5e

monitor_settings.py 以及 influx_settings.conf 代码，参考自小四毛，参考链接：https://github.com/xiaosimao/wx_code/tree/master/Crawler_Visualization

Grafana 是一个开源的分析和监控系统，拥有精美的web UI，支持多种图表，可以展示influxdb中存储的数据，并且有报警的功能。

Influxdb 是一款开源的时间序列数据库，专门用来存储和时间相关的数据（比如我用它存储某个时间点爬虫抓取信息的数量）。

设计原理：爬虫将抓取的数据写入MongoDB，InfluxDB从MongoDB获取数据抓取情况，Grafana 从 InfluxDB 中获取爬虫抓取数据情况并做图形化展示。

系统环境：MacOS High Sierra 10.12.6

2.Grafana介绍

Grafana简介：

-- Grafana 是一款采用 go 语言编写的开源应用；

-- Grafana 主要用于大规模指标数据的可视化展现；

-- Grafana有着非常漂亮的图表和布局展示，功能齐全的度量仪表盘和图形编辑器。

Grafana支持数据源：

-- Graphite；

-- Zabbix；

-- InfluxDB；

-- Prometheus；

-- OpenTSDB；

-- 最新版本4.3.1已经支持 MySQL 数据源。

Grafana 主要特性：

-- 灵活丰富的图形化选项；

-- 可以混合多种风格；

-- 支持多个数据源；

-- 拥有丰富的插件扩展；

-- 支持自动告警功能；

-- 支持用户权限管理。


3.InfluxDB介绍

InfluxDB 简介

-- InfluxDB 是一个当下比较流行的时序数据库；

-- InfluxDB 使用 Go 语言编写；

-- InfluxDB 无需外部依赖；

-- InfluxDB 适合构建大型分布式系统的监控系统。

主要特色功能：

-- 基于时间序列：支持与时间有关的相关函数（如最大，最小，求和等）；

-- 可度量性：可以实时对大量数据进行计算；

-- 基于事件：它支持任意的事件数据；
