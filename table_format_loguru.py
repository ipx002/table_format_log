# -*- coding:utf-8 -*-
"""
Time: 2026/3/28 22:52
Author: WuJunLin
FileName: table_format_loguru.py
"""
import sys
import pathlib
import traceback
import tabulate
from loguru import logger
from pyexpat.errors import messages


class TableFormatLoguru:
    last_stack_list = []

    @classmethod
    def get_stack_list(cls, record):
        stack = traceback.extract_stack()
        stack_list = []
        for frame in stack:
            stack_file_name = pathlib.Path(frame.filename).name
            record_file_name = pathlib.Path(record['file'].name).name
            stack_func_name = frame.name
            stack_file_line = frame.lineno
            record_file_line = record['line']
            record_func_name = record['function']
            stack_list.append(f'{stack_file_name}:{stack_func_name}:{stack_file_line}')
            if stack_list[-1] == f'{record_file_name}:{record_func_name}:{record_file_line}':
                # 调用栈到了日志记录的那一步，就可以了
                break

        # 立刻更新上一次的堆栈
        temp_stack_list = cls.last_stack_list.copy()
        cls.last_stack_list.clear()
        cls.last_stack_list = stack_list.copy()

        # 对余同一个位置连续的打印，调用堆栈可以不用这么复杂，适当简化
        stack_len = len(stack_list)
        last_stack_len = len(temp_stack_list)
        if (stack_len >= last_stack_len) and (stack_list[:last_stack_len] == temp_stack_list):
            stack_list = stack_list[last_stack_len:]

        return [record['thread'].name] + stack_list

    @classmethod
    def format_len(cls, input_str, target_len):
        """
        填充字符串的长度
        :param input_str:
        :param target_len:
        :return:
        """
        quot, mod = divmod(len(input_str), target_len)
        quot = quot + (1 if mod else 0)
        quot = quot + (0 if quot else 1)
        return input_str.ljust(target_len * quot, '.')

    @classmethod
    def format(cls, record):
        now_time = record['time'].strftime('%Y-%m-%d %H:%M:%S')
        now_time = f'{now_time},{str(record['time'].microsecond)[:-3]}'
        level_name = record['level'].name
        message = record['message']
        stack_list = cls.get_stack_list(record)

        time_len, level_len, stack_len = 23, 8, 40
        level_name = cls.format_len(level_name, level_len)
        stack_list = [cls.format_len(each, stack_len) for each in stack_list]
        stack_str = '\n'.join(stack_list)

        table = tabulate.tabulate(
            [[now_time, level_name, stack_str, message]],
            stralign='left',
            tablefmt='presto',
            maxcolwidths=[time_len, level_len, stack_len, None],
        )

        record['table_message'] = table
        return '<level>{table_message}</level>\n'


def main():
    logger.debug('debug message')
    logger.info('info message')
    logger.warning('warning message')
    logger.error('error message')
    logger.critical('critical message')

    logger.debug('debug message\nother line debug message')
    logger.info('info message\nother line info message')
    logger.warning('warning message\nother line warning')
    logger.error('error message\nother line error')
    logger.critical('critical message\nother line critical')

    for i in range(5):
        logger.debug(f'count {i} debug message')


if __name__ == '__main__':
    logger.remove()
    logger.add(sys.stderr, level="DEBUG", format=TableFormatLoguru.format)

    main()
