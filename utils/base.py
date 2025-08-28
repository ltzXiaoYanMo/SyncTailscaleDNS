from typing import Literal, TypeVar

record = TypeVar('record', bound=list[tuple[str, str, Literal["A", "AAAA"]]])

class BaseDns:
    """
    DNS操作基类，定义了DNS客户端的基本接口和通用功能
    """
    def __init__(self, config: dict, device: record) -> None:
        """
        你并不需要实现 __init__，仅在你需要存储新的变量时调用 super().__init__(config, device) 并添加新变量

        :param config: 来自 config.yaml 的配置字典，在主程序中已经获取
        :param device: 来自 Tailscale 的节点列表，格式为 [(hostname, ip, type), ...] 其中 type 为 "A" 或 "AAAA"，在主程序中已经获取
        """
        self.config = config
        self.device = device
        self.client = None  # DNS客户端实例，由具体子类创建
        self.id_map = {}  # 用于存储记录ID的映射，格式为 {(hostname, ip): record_id}，用处下面会说明
        self.create_client()

    def create_client(self) -> record:
        """
        创建DNS客户端实例，你必须实现该方法，本项目鼓励你使用服务商的 SDK 实现
        如果你的服务商实在没有 SDK 或者 SDK 太 shit 以至于你不得不使用 HTTP API，你可以这么写：
            self.client = httpx.Client()
            ...
            self.client.post(...)
        如果迫不得已，本项目鼓励使用 httpx 而不是 requests，以方便日后对异步的需求与支持
        """
        raise NotImplementedError


    def get_dns_list(self) -> record:
        """
        获取当前 DNS 记录列表，该方法应该由子类实现，用于从 DNS 服务商获取现有的 DNS 记录。

        注意：在这个方法中，你应该同步更新 id_map，如果你的服务商没有 RecordId 这种东西你也可以不更新。
        注意：id_map 的格式与本函数返回的格式有所差别，id_map 的 key 不包含 type

        :return DNS 现有记录
        """
        raise NotImplementedError

    def calc_diff(self, records: record) -> tuple[record, record]:
        """
        对比原先节点，找出差异。如果你遵守其他方法注释中的格式要求，那么你不需要自己再实现一遍。
        如果你迫不得已没有遵守其他方法注释中的要求，你需要自己实现

        :param records: DNS 记录，格式应为 [(hostname, content, type), ...]
        :returns: 返回两个列表，[0] 是未存在，需要添加的；[1] 是存在于 DNS，但这个设备已经被删除 / 发生变更，需要同步在 DNS 删除的
        """
        not_exist = [
            x for x in self.device if x not in records
        ]
        be_deleted = [
            x for x in records if x not in self.device
        ]
        return not_exist, be_deleted

    def add_record(self, hostname: str, ip: str, species: Literal["A", "AAAA"]) -> None:
        """
        添加DNS记录，该方法应该由子类实现，用于向DNS服务商添加新的DNS记录。

        :param hostname: 主机名，不包含域名部分
        :param ip: IP 地址
        :param species: 记录类型，"A" 或 "AAAA"
        """
        raise NotImplementedError

    def remove_record(self, hostname: str, ip: str) -> None:
        """
        删除DNS记录，该方法应该由子类实现，用于从DNS服务商删除指定的DNS记录。
        你可以使用 self.id_map 来获取 RecordID，如果你的服务商没有 RecordID 这种东西，你也可以不使用

        :param hostname: 主机名，不包含域名部分
        :param ip: IP 地址
        """
        raise NotImplementedError

    def execute(self) -> None:
        """
        执行DNS记录同步操作，该方法会调用其他方法来完成整个同步过程。如果你遵守其他方法注释中的格式要求，那么你不需要自己再实现一遍。
        如果你迫不得已没有遵守其他方法注释中的要求，你需要自己实现
        """
        records = self.get_dns_list()
        not_exist, be_deleted = self.calc_diff(records)
        for device in not_exist:
            self.add_record(device[0], device[1], device[2])

        for device in be_deleted:
            self.remove_record(device[0], device[1])
