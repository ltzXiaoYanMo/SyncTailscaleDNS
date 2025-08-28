import json
import sys

from loguru import logger
from tencentcloud.common import credential
from tencentcloud.common.profile.client_profile import ClientProfile
from tencentcloud.common.profile.http_profile import HttpProfile
from tencentcloud.dnspod.v20210323 import dnspod_client, models

from utils.base import BaseDns


class TencentCloudDns(BaseDns):
    """
    腾讯云 DNS（DNSPod）
    """
    def create_client(self):
        if (
                "access_key_id" not in self.config
                or "access_key_secret" not in self.config
        ):
            logger.error("错误：配置文件缺少必要的访问凭据")
            sys.exit(1)
        cred = credential.Credential(
            self.config["access_key_id"],
            self.config["access_key_secret"]
        )
        http_profile = HttpProfile()
        http_profile.endpoint = "dnspod.tencentcloudapi.com"
        client_profile = ClientProfile()
        client_profile.httpProfile = http_profile
        self.client = dnspod_client.DnspodClient(cred, "", client_profile)

    def get_dns_list(self):
        req = models.DescribeRecordListRequest()
        params = {
            "Domain": self.config['domain_name']
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.DescribeRecordList(req)
        logger.debug(resp)
        results = []
        for i in resp.RecordList:
            if i.Type not in ['A', 'AAAA']:
                continue
            results.append(
                (
                    i.Name,  # 孩子们他来了吗，如来
                    i.Value,
                    i.Type
                )
            )
            self.id_map[(i.Name, i.Value)] = i.RecordId
        return results

    def add_record(self, hostname, ip, species):
        req = models.CreateRecordRequest()
        params = {
            "Domain": self.config['domain_name'],
            "RecordType": species,
            "RecordLine": "默认",
            "Value": ip,
            "SubDomain": hostname
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.CreateRecord(req)
        logger.info(
            f"成功添加{species}记录: {hostname} -> {ip} (记录ID: {resp.RecordId})"
        )

    def remove_record(self, hostname, ip):
        req = models.DeleteRecordRequest()
        params = {
            "Domain": self.config['domain_name'],
            "RecordId": self.id_map[(hostname, ip)]
        }
        req.from_json_string(json.dumps(params))
        resp = self.client.DeleteRecord(req)
        logger.info(
            f"成功删除解析记录: {hostname} -> {ip} (请求ID: {resp.RequestId})"
        )
