import pathlib
import coredumpy
import yaml
import sys
from loguru import logger
from utils import list_node, BaseDns, AliDns, CloudflareDns, TencentCloudDns
from typing import Type

coredumpy.patch_except(directory='./dumps')

cls_map: dict[str, Type[BaseDns]] = {
    'alidns': AliDns,
    'cloudflare': CloudflareDns,
    'dnspod': TencentCloudDns
}

def main():
    config = pathlib.Path("config.yaml")
    if not config.exists():
        config.write_text(
            """dns_provider: alidns # dns_provider e.g. alidns
zone_id:
domain_name:
access_key_id:
access_key_secret:
cloudflare_api_token:
""",
        )
        logger.error("错误：找不到配置文件 config.yaml，已自动生成文件")
        sys.exit(1)
    config_data = yaml.safe_load(config.read_text())
    if 'dns_provider' not in config_data:
        logger.error("错误：配置文件缺少必要的 dns_provider 字段")
        sys.exit(1)
    if 'domain_name' not in config_data:
        logger.error("错误：配置文件缺少必要的 domain_name 字段")
        sys.exit(1)
    devices_data = list_node()
    provider = config_data['dns_provider']
    if provider not in cls_map:
        logger.error(f"尚不支持对 {provider} 的支持")
        sys.exit(0)
    cls_map[provider](config_data, devices_data).execute()


if __name__ == "__main__":
    main()
