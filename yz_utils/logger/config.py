#!/usr/bin/env python3.5+
# -*- coding: utf-8 -*-
"""
@auth: cml
@date: 2019-07-10
@desc: ...

日志的配置参数，日志对象主要有3个子模块，分别为
    - formaters（输出格式）
    - handlers（日志操作类型）
    - loggers（日志记录器的名称）

其中hadlers为日志的具体执行，依赖于formaters和日志操作类型或一些属性，
比如按大小分片还是时间分片，是写入还是打印到控制台。
logger负责调用handle，一个logger可以调用多个handler，
比如logger.info调用了打印到控制台handler（logging.StreamHandler）
和写入到文件handler（mlogging.TimedRotatingFileHandler_MP），
在没有指定logger名字的时候，即logger=logging.get_logger()的时候，
logger会自动选择名为root的logger

format: 日志消息格式
格式                 描述
%(name)s            记录器的名称
%(levelno)s         数字形式的日志记录级别
%(levelname)s       日志记录级别的文本名称
%(filename)s        执行日志记录调用的源文件的文件名称
%(pathname)s        执行日志记录调用的源文件的路径名称
%(funcName)s        执行日志记录调用的函数名称
%(module)s          执行日志记录调用的模块名称
%(lineno)s          执行日志记录调用的行号
%(created)s         执行日志记录的时间
%(asctime)s         日期和时间
%(msecs)s           毫秒部分
%(thread)d          线程ID
%(threadName)s      线程名称
%(process)d         进程ID
%(message)s         记录的消息
"""
import os
import sys
curr_path = os.path.abspath(os.path.dirname(os.curdir))
sys.path.append(curr_path)
# _path = os.path.join(os.path.dirname(os.path.dirname(curr_path)), 'output')
LOG_PATH = os.path.join(curr_path, 'logs')
# from app.settings import log_conf
# LOG_PATH = log_conf.get('log_path')
print("====>log_path:", LOG_PATH)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,  # 不禁用完成配置之前创建的所有日志处理器
    "formatters": {
        "simple": {
            # 简单的输出模式
            'format': '%(asctime)s | %(levelname)s | PID:%(process)d | TID:%(threadName)s | [%(module)s: %(funcName)s] | - %(message)s'
        },
        'standard': {
            # 较为复杂的输出模式，可以进行自定义
            'format': '%(asctime)s | %(levelname)s | PID:%(process)d | TID:%(threadName)s | [%(module)s: %(funcName)s] | - %(message)s'
        },
    },

    # 过滤器
    "filters": {
        'debug_filter': {
            '()': 'rbcomm.logger.filters.DebugFilter'
        },
        'info_filter': {
            '()': 'rbcomm.logger.filters.InfoFilter'
        },
        'warning_filter': {
            '()': 'rbcomm.logger.filters.WarningFilter'
        },
        'error_filter': {
            '()': 'rbcomm.logger.filters.ErrorFilter'
        },
        'critical_filter': {
            '()': 'rbcomm.logger.filters.CriticalFilter'
        },
        'no_debug_filter': {
            '()': 'rbcomm.logger.filters.NoDebugFilter'
        }
    },
    "handlers": {
        # # 输出到控制台的handler
        # "console": {
        #     # 定义输出流的类
        #     "class": "logging.StreamHandler",
        #     # handler等级，如果实际执行等级高于此等级，则不触发handler
        #     "level": "DEBUG",
        #     # 输出的日志格式
        #     "formatter": "simple",
        #     # 流调用系统输出
        #     "stream": "ext://sys.stdout"
        # },
        # # 写入到文件的hanler，写入等级为info，命名为request是为了专门记录一些网络请求日志
        # "file": {
        #     # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
        #     "class": "handlers.TimedRotatingFileHandlerMP",
        #     # 日志等级
        #     "level": "DEBUG",
        #     # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
        #     "formatter": "standard",
        #     # 要写入的文件名
        #     "filename": os.path.join(LOG_PATH, 'default', 'info.log'),
        #     # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
        #     # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
        #     "when": 'D',
        #     'backupCount': 5,  # 备份份数
        #     "encoding": "utf8",
        #     "filters": ["info_filter"]
        # },
        # "info_file": {
        #     "class": "handlers.TimedRotatingFileHandlerMP",
        #     "level": "INFO",
        #     "formatter": "standard",
        #     "filename": os.path.join(LOG_PATH, 'default', 'info.log'),
        #     "when": 'D',
        #     'backupCount': 5,  # 备份份数
        #     "encoding": "utf8",
        #     "filters": ["info_filter"]
        # },
        # "err_file": {
        #     "class": "handlers.TimedRotatingFileHandlerMP",
        #     "level": "WARN",
        #     "formatter": "standard",
        #     "filename": os.path.join(LOG_PATH, 'default', 'error.log'),
        #     "when": 'D',
        #     'backupCount': 5,  # 备份份数
        #     "encoding": "utf8",
        #     "filters": ["info_filter"]
        # },
    },
    # "loggers": {},
    "loggers": {
        # # logger名字
        # "default_logger": {
        #     # logger集成的handler
        #     'handlers': ['console', 'file'],
        #     # logger等级，如果实际执行等级，高于此等级，则不触发此logger，logger中所有的handler均不会被触发
        #     'level': "DEBUG",
        #     # 是否继承root日志，如果继承，root的handler会加入到当前logger的handlers中
        #     'propagate': False
        # },
        # "debug_logger": {
        #     'handlers': ['console', 'debug_file'],
        #     'level': "DEBUG",
        #     'propagate': False
        # },
        # "info_logger": {
        #     'handlers': ['console', 'info_file'],
        #     'level': "INFO",
        #     'propagate': False
        # },
        # "warn_logger": {
        #     'handlers': ['console', 'err_file'],
        #     'level': "WARN",
        #     'propagate': False
        # },
        # "error_logger": {
        #     'handlers': ['console', 'err_file'],
        #     'level': "ERROR",
        #     'propagate': False
        # },
        # "critical_logger": {
        #     'handlers': ['console', 'err_file'],
        #     'level': "DEBUG",
        #     'propagate': False
        # },
    },
    # 基础logger，当不指定logger名称时，默认选择此logger
    # "root": {
    #     'handlers': ['file'],
    #     'level': "DEBUG",
    #     'propagate': True
    # }
}
