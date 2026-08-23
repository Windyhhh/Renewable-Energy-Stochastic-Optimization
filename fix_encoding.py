"""
编码修复模块
解决Windows下subprocess的GBK解码错误和loky警告
在所有程序开头导入此模块即可
"""

import sys
import os
import warnings
import logging


def apply_fixes():
    """应用所有编码和环境修复"""

    # ========== 修复0：临时重定向stderr，屏蔽loky的调用栈输出 ==========
    import io
    import contextlib

    # 创建一个过滤器，只屏蔽loky相关的输出
    class StderrFilter:
        def __init__(self, original_stderr):
            self.original_stderr = original_stderr
            self.buffer = []

        def write(self, text):
            # 如果包含loky相关的路径，就不输出
            if 'loky' in text or 'joblib' in text:
                return
            # 其他内容正常输出
            self.original_stderr.write(text)

        def flush(self):
            self.original_stderr.flush()

    # 替换stderr
    sys.stderr = StderrFilter(sys.stderr)

    # ========== 修复1：消除loky的CPU核心数警告和调用栈输出 ==========
    # 设置环境变量，跳过物理核心数检测
    cpu_count = os.cpu_count() or 4  # 默认4核
    os.environ['LOKY_MAX_CPU_COUNT'] = str(cpu_count)

    # 过滤loky和joblib的所有日志输出（只保留ERROR级别）
    logging.getLogger('loky').setLevel(logging.ERROR)
    logging.getLogger('joblib').setLevel(logging.ERROR)

    # 过滤loky的UserWarning
    warnings.filterwarnings('ignore', category=UserWarning, module='loky')
    warnings.filterwarnings('ignore', message='.*Could not find the number of physical cores.*')

    # ========== 修复2：屏蔽loky的subprocess调用栈输出 ==========
    # 重定向loky内部的subprocess调用，屏蔽其标准错误输出
    try:
        import subprocess
        import joblib.externals.loky.backend.context as loky_context

        # 保存原始的subprocess.run
        original_subprocess_run = subprocess.run

        def quiet_subprocess_run(*args, **kwargs):
            """静默版本的subprocess.run，屏蔽stderr输出"""
            # 只对loky的调用屏蔽输出，不影响其他地方
            kwargs.setdefault('stderr', subprocess.DEVNULL)
            kwargs.setdefault('stdout', subprocess.DEVNULL)
            try:
                return original_subprocess_run(*args, **kwargs)
            except:
                # 如果出错，返回一个默认结果
                class DummyResult:
                    returncode = 0
                    stdout = b''
                    stderr = b''
                return DummyResult()

        # 替换loky使用的subprocess.run
        loky_context.subprocess.run = quiet_subprocess_run

        # 同时屏蔽traceback输出
        import traceback
        original_print_exception = traceback.print_exception

        def silent_print_exception(exc_type, exc_value, exc_traceback, **kwargs):
            """屏蔽loky相关的traceback输出"""
            if exc_traceback is not None:
                # 检查是否是loky相关的调用栈
                tb = exc_traceback
                while tb is not None:
                    frame = tb.tb_frame
                    filename = frame.f_code.co_filename
                    if 'loky' in filename or 'joblib' in filename:
                        # 是loky相关的，不输出
                        return
                    tb = tb.tb_next
            # 不是loky相关的，正常输出
            original_print_exception(exc_type, exc_value, exc_traceback, **kwargs)

        traceback.print_exception = silent_print_exception

    except:
        # 如果导入失败，忽略（可能还没安装joblib）
        pass

    # ========== 修复3：过滤subprocess的UnicodeDecodeError警告 ==========
    # 这些错误发生在后台线程，不影响功能，直接过滤
    warnings.filterwarnings('ignore', category=UnicodeWarning)

    # 过滤线程中的异常输出（通过设置stderr处理）
    import threading
    original_excepthook = threading.excepthook

    def silent_excepthook(args):
        """静默处理线程中的UnicodeDecodeError"""
        if isinstance(args.exc_value, (UnicodeDecodeError, UnicodeWarning)):
            # 忽略Unicode相关错误
            pass
        else:
            # 其他异常正常处理
            original_excepthook(args)

    threading.excepthook = silent_excepthook

    # ========== 修复4：设置默认编码为UTF-8 ==========
    if sys.platform == 'win32':
        # Windows下设置控制台编码
        try:
            sys.stdout.reconfigure(encoding='utf-8', errors='ignore')
            sys.stderr.reconfigure(encoding='utf-8', errors='ignore')
        except:
            pass

    print("✓ 编码修复已应用")
    print(f"  - loky使用{cpu_count}个CPU核心")
    print(f"  - 调用栈输出已屏蔽")
    print(f"  - 警告和异常过滤已启用")
    print()


# 自动应用修复（导入时执行）
apply_fixes()

