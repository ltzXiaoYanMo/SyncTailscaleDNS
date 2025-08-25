import portalocker


def safe_file_write(filename: str, s, mode: str = "w", encode: str = "UTF-8"):
    # 参数验证
    if not filename:
        raise ValueError("filename cannot be empty")

    # 确定是否需要编码参数
    open_kwargs = {}
    if "b" not in mode:
        open_kwargs["encoding"] = encode

    # 文件写入和锁操作
    with open(filename, mode, **open_kwargs) as file:
        try:
            portalocker.lock(file, portalocker.LOCK_EX)
            file.write(s)
        finally:
            try:
                portalocker.unlock(file)
            except:
                pass  # 忽略 unlock 操作的异常
