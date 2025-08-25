import sys

from loguru import logger
from alibabacloud_alidns20150109.client import Client as Alidns20150109Client
from alibabacloud_tea_openapi import models as open_api_models
from alibabacloud_alidns20150109 import models as alidns_20150109_models
from alibabacloud_tea_util import models as util_models

from utils.base import BaseDns


class AliDns(BaseDns):
    """
    阿里云DNS操作示例类
    用于创建DNS记录，支持A记录(IPv4)和AAAA记录(IPv6)
    """
    def create_client(self):
        if (
                "access_key_id" not in self.config
                or "access_key_secret" not in self.config
        ):
            logger.error("错误：配置文件缺少必要的访问凭据")
            sys.exit(1)
        config = open_api_models.Config(
            access_key_id=self.config["access_key_id"],
            access_key_secret=self.config["access_key_secret"],
        )
        config.endpoint = "alidns.cn-hangzhou.aliyuncs.com"  # 默认为杭州
        self.client =  Alidns20150109Client(config)

    def get_dns_list(self):
        req = alidns_20150109_models.DescribeDomainRecordsRequest()
        req.domain_name = self.config['domain_name']
        resp = self.client.describe_domain_records(req).to_map()
        logger.debug(resp)
        results = []
        for i in resp['body']['DomainRecords']['Record']:
            if i['Type'] not in ['A', 'AAAA']:
                continue
            results.append(
                (
                    i['RR'],  # 孩子们他来了吗，如来
                    i['Value'],
                    i['Type']
                )
            )
            self.id_map[(i['RR'], i['Value'])] = i['RecordId']
        return results

    def add_record(self, hostname, ip, species):
        """
        为指定设备添加AAAA记录(IPv6)
        """
        add_domain_record_request = alidns_20150109_models.AddDomainRecordRequest(
            domain_name=self.config['domain_name'],
            rr=hostname,
            type=species,
            value=ip,
        )
        runtime = util_models.RuntimeOptions()
        response = self.client.add_domain_record_with_options(
            add_domain_record_request, runtime
        )
        logger.info(
            f"成功添加{species}记录: {hostname} -> {ip} (记录ID: {response.body.record_id})"
        )

    def remove_record(self, hostname, ip):
        req = alidns_20150109_models.DeleteDomainRecordRequest(
            record_id=self.id_map[(hostname, ip)]
        )
        runtime = util_models.RuntimeOptions()
        response = self.client.delete_domain_record_with_options(
            req, runtime
        )
        logger.info(
            f"成功删除解析记录: {hostname} -> {ip} (记录ID: {response.body.record_id})"
        )
