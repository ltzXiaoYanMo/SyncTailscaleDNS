"""
Docs: https://developers.cloudflare.com/api/python/resources/dns/subresources/records/methods/batch/
API：https://api.cloudflare.com/client/v4/zones/$ZONE_ID/dns_records/batch
"""
from loguru import logger
from utils.base import BaseDns
from cloudflare import Cloudflare


class CloudflareDns(BaseDns):
    def create_client(self):
        self.client = Cloudflare(
            api_token=self.config['cloudflare_api_token'],
        )


    def get_dns_list(self):
        response = self.client.dns.records.list(
            zone_id=self.config['zone_id'],
            per_page=114514  # maximum: 5000000
        )
        result = []
        for i in response.result:
            if i.type not in ['A', 'AAAA'] or i.name == self.config['domain_name']:
                continue
            result.append((i.name[:-len(self.config['domain_name']) - 1], i.content, i.type))
            self.id_map[(i.name[:-len(self.config['domain_name']) - 1], i.content)] = i.id
        return result

    def calc_diff(self, records: list):
        not_exist = [
            x for x in self.device if x not in records
        ]
        be_deleted = [
            x for x in records if x not in self.device
        ]
        return not_exist, be_deleted

    def add_record(self, hostname, ip, species):
        # 这边吧我也不知道为什么类型检查器会报错，但又确实能跑
        # noinspection PyTypeChecker
        record = self.client.dns.records.create(
            zone_id=str(self.config['zone_id']),
            name=f"{hostname}.{self.config['domain_name']}",
            content=ip,
            ttl=1,
            type=species
        )
        logger.info(
            f"成功添加{species}记录: {hostname} -> {ip} (记录ID: {record.id})"
        )

    def remove_record(self, hostname, ip):
        logger.debug(f'{hostname = }, {ip = }')
        record = self.client.dns.records.delete(
            dns_record_id=self.id_map[hostname, ip],
            zone_id=self.config['zone_id'],
        )
        logger.info(
            f"成功删除解析记录: {hostname} -> {ip} (记录ID: {record.id})"
        )
