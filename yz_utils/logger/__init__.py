#!/usr/bin/env python3.5+
# -*- coding: utf-8 -*-
"""
@auth: cml
@date: 2019-07-10
@desc: 根据应用来分类日志，每个应用下都有六种日志模式：
        ['debug', 'request', 'warning', 'error', 'critical', 'request']

"""
import os
import sys
sys.path.append(os.path.dirname(os.pardir))

import re
SYS_ENV = 'win' if re.search('[Ww]in', sys.platform) else 'unix'

import logging
from .config import LOG_PATH, LOGGING_CONFIG

# from logging.config import dictConfig
# from logging.handlers import TimedRotatingFileHandler


class Logger:
    __instance = {}  # 单例模式存储对象
    __is_init = False  # 防止重复初始化

    def __new__(cls, app_name='default', *args, **kwargs):
        """对于每个app_name单例模式"""
        if app_name not in cls.__instance:
            cls.__instance[app_name] = super().__new__(cls)
        return cls.__instance[app_name]

    def __init__(self, app_name='default', 
                 log_config=LOGGING_CONFIG, 
                 log_path=LOG_PATH, 
                 is_debug=True):
        """初始化logger，通过LOGGING配置logger"""
        if self.__is_init is True:
            return
        self.log_path = log_path
        log_file_dir = os.path.join(self.log_path, app_name)
        print("初始化%s的logger，日志写入：%s 文件夹下" % (app_name, log_file_dir))
        self.__is_init = True
        self.app_name = app_name
        self.is_debug = is_debug
        self.log_config = log_config

        # 默认路径为当前项目根目录下的logs/${app_name}
        self.log_cur_path = os.path.join(self.log_path, self.app_name)
        self.mkdir_log_path()
        self.configure_logging()

    def mkdir_log_path(self):
        if not os.path.exists(self.log_cur_path):  # 不存在就创建default目录
            os.makedirs(self.log_cur_path)

    def configure_logging(self):
        # logging.addLevelName(TRACE_LOG_LEVEL, "TRACE")
        if sys.version_info < (3, 7):
            # https://bugs.python.org/issue30520
            import pickle
            import logging

            def __reduce__(self):
                if isinstance(self, logging.RootLogger):
                    return logging.getLogger, ()

                if logging.getLogger(self.name) is not self:
                    raise pickle.PicklingError("logger cannot be pickled")
                return logging.getLogger, (self.name,)

            logging.Logger.__reduce__ = __reduce__

        # 日志名和日志等级的映射
        log_levels = ['debug', 'info', 'warning', 'error', 'critical']

        # 根据app_name动态更新LOGGING_CONFIG配置，为每个app_name创建文件夹，配置handler
        for level in log_levels:
            handler_name = '%s_%s' % (self.app_name, level)
            if level == 'debug':
                self.log_config['handlers'][
                    handler_name] = self.get_console_handler_conf()
            else:
                filename = os.path.join(self.log_cur_path, (level + '.log'))
                lev_up = level.upper()
                self.log_config['handlers'][
                    handler_name] = self.get_file_handler_conf(
                    filename=filename, level=lev_up)

        # 添加app logger及app_request logger
        logger_name = '%s_logger' % self.app_name
        self.log_config['loggers'][logger_name] = self.get_logger_conf(
            app_name=self.app_name)

        # 将LOGGING_CONFIG中的配置信息更新到logging中
        if self.log_config is not None:
            from logging import config
            if isinstance(self.log_config, dict):
                config.dictConfig(self.log_config)
            else:
                config.fileConfig(self.log_config)
        # dictConfig(LOGGING_CONFIG)

    def get_console_handler_conf(self):
        console_handler_conf = {
            # 定义输出流的类
            "class": "logging.StreamHandler",
            # handler等级，如果实际执行等级高于此等级，则不触发handler
            "level": "DEBUG",
            # 输出的日志格式
            "formatter": "simple",
            # 流调用系统输出
            "stream": "ext://sys.stdout"
        }
        if self.is_debug:
            console_handler_conf['filters'] = ['debug_filter']
        else:
            console_handler_conf['filters'] = ['no_debug_filter']
        return console_handler_conf

    @staticmethod
    # 写入文件handler配置
    def get_file_handler_conf(filename: str, level='INFO'):
        file_handler_conf = {
            # 定义写入文件的日志类，此类为按时间分割日志类，还有一些按日志大小分割日志的类等
            "class": "rbcomm.logger.handlers.TimedRotatingFileHandlerMP",
            # 日志等级
            "level": "",
            # 日志写入格式，因为要写入到文件后期可能会debug用，所以用了较为详细的standard日志格式
            "formatter": "standard",
            # 要写入的文件名
            "filename": '',
            # 分割单位，D日，H小时，M分钟，W星期，一般是以小时或天为单位
            # 比如文件名为test.log，到凌晨0点的时候会自动分离出test.log.yyyy-mm-dd
            "when": 'D',
            'backupCount': 5,  # 备份份数
            "encoding": "utf8",
            "filters": []
        }
        if SYS_ENV == 'win':
            file_handler_conf[
                'class'] = 'logging.handlers.TimedRotatingFileHandler'
        filters = ['%s_filter' % (level.lower())]
        update_dict = {'filename': filename, 'level': level, 'filters': filters}
        file_handler_conf.update(update_dict)
        return file_handler_conf

    @staticmethod
    def get_logger_conf(app_name='default'):
        """ logger 配置"""
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        # 如果只是debug级别logger，只配置打印handler，不会记录到文件中
        log_levels = ['debug', 'info', 'warning', 'error', 'critical']
        logger_conf['handlers'] = ['%s_%s' % (app_name, level) for level in
                                   log_levels]
        return logger_conf

    @staticmethod
    # request logger配置
    def get_request_logger_conf(app_name='default'):
        logger_conf = {
            'handlers': [],
            'level': "DEBUG",
            'propagate': False
        }
        log_levels = ['debug', 'request', 'warning', 'error', 'critical']
        logger_conf['handlers'] = ['%s_%s' % (app_name, level) for level in
                                   log_levels]
        return logger_conf


# 获取日常logger
def get_logger(app_name: str, is_debug=True):
    Logger(app_name, is_debug=is_debug)
    logger_name = '%s_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


# 获取request logger
def get_request_logger(app_name: str, is_debug=True):
    Logger(app_name, is_debug=is_debug)
    logger_name = '%s_request_logger' % app_name
    logger = logging.getLogger(logger_name)
    return logger


if __name__ == '__main__':
    # 单例模式测试
    logger = get_request_logger('cml_test', is_debug=True)

    logger.error('error log')
    logger.debug('debug log')
    logger.debug('debug log')