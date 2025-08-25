from typing import Literal


class BaseDns:
    """
    DNS操作基类，定义了DNS客户端的基本接口和通用功能
    """
    def __init__(self, config: dict, device: list):
        """
        初始化DNS客户端

        Args:
            config: dict, 配置字典，包含DNS服务商的认证信息和其他配置
            device: list, 设备列表，包含需要管理的设备信息
        """
        self.config = config
        self.device = device
        self.client = None  # DNS客户端实例，由具体子类创建
        self.id_map = {}
        self.create_client()

    def create_client(self):
        """
        创建DNS客户端实例
        """
        raise NotImplementedError


    def get_dns_list(self):
        """
        获取当前DNS记录列表
        该方法应该由子类实现，用于从DNS服务商获取现有的DNS记录。
        """
        raise NotImplementedError

    def calc_diff(self, records: list[tuple[str, str, Literal["A", "AAAA"]]]):
        """
        对比原先节点
        :param records: DNS 记录，格式应为 (hostname, content, type)
        :return:
        """
        not_exist = [
            x for x in self.device if x not in records
        ]
        be_deleted = [
            x for x in records if x not in self.device
        ]
        return not_exist, be_deleted

    def add_record(self, hostname: str, ip: str, species: Literal["A", "AAAA"]):
        """
        添加DNS记录
        该方法应该由子类实现，用于向DNS服务商添加新的DNS记录。

        Args:
            hostname: str, 主机名（如：example.com）
            ip: str, IP地址（如：192.168.1.1）
            species: str, 记录类型（如：A、AAAA）

        Raises:
            NotImplementedError: 如果子类没有实现此方法
        """
        raise NotImplementedError

    def remove_record(self, hostname: str, ip: str):
        raise NotImplementedError

    def execute(self):
        """
        执行DNS记录同步操作
        """
        records = self.get_dns_list()
        not_exist, be_deleted = self.calc_diff(records)
        for device in not_exist:
            self.add_record(device[0], device[1], device[2])

        for device in be_deleted:
            self.remove_record(device[0], device[1])
