import sys
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models


class Sample:
    """
    阿里云DNS操作示例类
    用于创建DNS记录，支持A记录(IPv4)和AAAA记录(IPv6)
    """

    def __init__(self):
        """
        初始化方法
        当前实现为空，可根据需要添加初始化逻辑
        """
        pass

    @staticmethod
    def create_client(config_data: dict) -> Alidns20150109Client:
        """
        创建阿里云DNS客户端

        Args:
            config_data (dict): 包含访问凭证的配置字典
                - access_key_id: 阿里云访问密钥ID
                - access_key_secret: 阿里云访问密钥

        Returns:
            Alidns20150109Client: 阿里云DNS客户端实例

        Raises:
            SystemExit: 当缺少必要配置或创建客户端失败时退出程序
        """
        try:
            if (
                "access_key_id" not in config_data
                or "access_key_secret" not in config_data
            ):
                print("错误：配置文件缺少必要的访问凭据")
                sys.exit(1)

            config = open_api_models.Config(
                access_key_id=config_data["access_key_id"],
                access_key_secret=config_data["access_key_secret"],
            )
            config.endpoint = "alidns.cn-hangzhou.aliyuncs.com"  # 默认为杭州
            return Alidns20150109Client(config)
        except Exception as e:
            print(f"创建客户端时出错：{str(e)}")
            sys.exit(1)

    @staticmethod
    def _add_a_record(client, domain_name, hostname, ipv4):
        """
        为指定设备添加A记录(IPv4)

        Args:
            client: 阿里云DNS客户端实例
            domain_name: 域名
            hostname: 主机名
            ipv4: IPv4地址
        """
        try:
            add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
                domain_name=domain_name, rr=hostname, type="A", value=ipv4
            )
            runtime = util_models.RuntimeOptions()
            response = client.add_domain_record_with_options(
                add_domain_record_request, runtime
            )
            print(
                f"成功添加A记录: {hostname} -> {ipv4} (记录ID: {response.body.record_id})"
            )
        except Exception as error:
            print(f"添加A记录失败: {hostname} -> {ipv4}")
            print(f"错误信息: {str(error)}")
            if hasattr(error, "data"):
                print(f"诊断建议: {error.data.get('Recommend')}")

    @staticmethod
    def _add_aaaa_record(client, domain_name, hostname, ipv6):
        """
        为指定设备添加AAAA记录(IPv6)

        Args:
            client: 阿里云DNS客户端实例
            domain_name: 域名
            hostname: 主机名
            ipv6: IPv6地址
        """
        try:
            add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
                domain_name=domain_name,
                rr=hostname,
                type="AAAA",
                value=ipv6,
            )
            runtime = util_models.RuntimeOptions()
            response = client.add_domain_record_with_options(
                add_domain_record_request, runtime
            )
            print(
                f"成功添加AAAA记录: {hostname} -> {ipv6} (记录ID: {response.body.record_id})"
            )
        except Exception as error:
            print(f"添加AAAA记录失败: {hostname} -> {ipv6}")
            print(f"错误信息: {str(error)}")
            if hasattr(error, "data"):
                print(f"诊断建议: {error.data.get('Recommend')}")

    @staticmethod
    def main(config_data: dict, devices_data: dict) -> None:
        """
        主函数：为设备添加DNS记录
        支持为每个设备的IPv4和IPv6地址分别创建A记录和AAAA记录

        Args:
            config_data (dict): 配置信息，包含访问凭证和域名
            devices_data (dict): 设备信息，包含设备主机名和IP地址列表
        """

        # 创建客户端
        client = Sample.create_client(config_data)

        # 获取域名（从配置文件或使用默认值）
        domain_name = config_data.get("domain_name")

        # 为每个设备添加DNS记录
        for device in devices_data["devices"]:
            hostname = device["hostname"]
            ipv4_addresses = device.get("ipv4_addresses", [])
            ipv6_addresses = device.get("ipv6_addresses", [])

            # 为每个IPv4地址添加A记录
            for ipv4 in ipv4_addresses:
                Sample._add_a_record(client, domain_name, hostname, ipv4)

            # 为每个IPv6地址添加AAAA记录
            for ipv6 in ipv6_addresses:
                Sample._add_aaaa_record(client, domain_name, hostname, ipv6)
