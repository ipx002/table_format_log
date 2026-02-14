import pathlib
import logging
import colorama
import traceback
import tabulate


class TabulateFormatter(logging.Formatter):
    last_stack_list = []

    def get_stack_list(self, record: logging.LogRecord):
        stack = traceback.extract_stack()
        stack_list = []
        for frame in stack:
            stack_file_name = pathlib.Path(frame.filename).name
            record_file_name = pathlib.Path(record.filename).name
            stack_file_line = frame.lineno
            record_file_line = record.lineno
            stack_list.append(f'{stack_file_name}:{stack_file_line}')
            if stack_list[-1] == f'{record_file_name}:{record_file_line}':
                break

        # 立刻更新上一次的堆栈
        temp_stack_list = self.last_stack_list.copy()
        self.last_stack_list.clear()
        self.last_stack_list = stack_list.copy()

        stack_len = len(stack_list)
        last_stack_len = len(temp_stack_list)
        if (stack_len >= last_stack_len) and (stack_list[:last_stack_len] == temp_stack_list):
            stack_list = stack_list[last_stack_len:]

        return [record.threadName] + stack_list

    @staticmethod
    def format_len(input_str, target_len):
        quot, mod = divmod(len(input_str), target_len)
        quot = quot + (1 if mod else 0)
        quot = quot + (0 if quot else 1)
        return input_str.ljust(target_len * quot, '.')


    def format(self, record):
        now_time = self.formatTime(record, self.datefmt)
        level_name = record.levelname
        message = record.getMessage()
        stack_list = self.get_stack_list(record)

        time_len, level_len, stack_len = 23, 8, 25
        level_name = self.format_len(level_name, level_len)
        stack_list = [self.format_len(each, stack_len) for each in stack_list]
        stack_str = '\n'.join(stack_list)

        table = tabulate.tabulate(
            [[now_time, level_name, stack_str, message]],
            stralign='left',
            tablefmt='presto',
            maxcolwidths=[time_len, level_len, stack_len, None],
        )

        return table


class ColorTabulateFormatter(TabulateFormatter):
    colorama.init(autoreset=True)
    color_map = {
        logging.DEBUG: colorama.Fore.WHITE,
        logging.INFO: colorama.Fore.GREEN,
        logging.WARNING: colorama.Fore.YELLOW,
        logging.ERROR: colorama.Fore.RED,
        logging.CRITICAL: colorama.Fore.MAGENTA,
    }
    def format(self, record):
        table = super().format(record)
        table_list = table.splitlines(False)
        table_list = [self.color_map[record.levelno] + each for each in table_list]
        table = '\n'.join(table_list)
        return table
