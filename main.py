import yaml
import sys
import modules
from loguru import logger
from modules.addRecordAliDNS import Sample
from modules.listNodes import list_node


def main():
    try:
        # 读取配置文件
        with open("config.yaml", "r", encoding="utf-8") as f:
            config_data = yaml.safe_load(f)

        # 获取设备列表
        devices_data = list_node(config_data)

        # 添加DNS记录
        Sample.main(config_data, devices_data)

    except FileNotFoundError:
        modules.safe_file_write(
            "config.yaml",
            """dns_provider: alidns # dns_provider e.g. alidns
access_key_id: # if you use alidns, you need to set this value
access_key_secret: # if you use alidns, you need to set this value
domain_name:""",
        )
        logger.error("错误：找不到配置文件 config.yaml，已自动生成文件")
        sys.exit(1)
    except Exception as e:
        logger.error(f"执行过程中出错：{str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
