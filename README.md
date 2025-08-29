# SyncTailscaleDNS
[![State-of-the-art Shitcode](http://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode) | [![Quality Gate Status](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=alert_status)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Bugs](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=bugs)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Code Smells](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=code_smells)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Coverage](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=coverage)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Duplicated Lines (%)](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=duplicated_lines_density)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Lines of Code](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=ncloc)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Reliability Rating](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=reliability_rating)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=security_rating)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Technical Debt](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=sqale_index)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Maintainability Rating](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=sqale_rating)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns) | [![Vulnerabilities](https://sonarcloud.io/api/project_badges/measure?project=ltzxiaoyanmo_synctailscaledns&metric=vulnerabilities)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns)

[![Quality gate](https://sonarcloud.io/api/project_badges/quality_gate?project=ltzxiaoyanmo_synctailscaledns)](https://sonarcloud.io/summary/new_code?id=ltzxiaoyanmo_synctailscaledns)

## 项目简介
SyncTailscaleDNS 用于自动将 Tailscale 网络中的节点 IP（A/AAAA 记录）同步到公网 DNS（如 DNSPod、阿里云 DNS、Cloudflare）。解决 Tailscale 的 MagicDNS 老是爆炸的问题。

## 主要功能
- 获取 Tailscale 网络节点的 DNS 名称和 IP（支持 IPv4/IPv6）
- 支持将节点信息同步到阿里云 DNS 或 Cloudflare DNS
- 支持多种 DNS 服务商，代码易于扩展

## 安装与依赖
- Python 3
  - 开发环境为 Python 3.12.10，建议使用 3.12+
- Tailscale CLI
- Python UV

```bash
uv sync
```

## 使用方法
```bash
uv run python main.py
```

1. 运行前需配置 config.yaml（首次运行会自动生成模板） 
2. 根据下文中的配置说明写配置文件
3. Just Do it!

> [!IMPORTANT]
> 每次执行只会同步当前 Tailscale 网络中的节点，不会循环执行
> 
> 如果需要定时执行，请使用系统的定时任务工具（如 cron）
> 
> 不建议混用域名，请使用一个单独的域名进行操作，否则有误删其他正常解析记录的风险

## 配置说明（config.yaml 示例）
```yaml
dns_provider: alidns # 可选： alidns / cloudflare / dnspod
zone_id: <你的DNS区域ID>  # 若你使用 Cloudflare，否则留空
domain_name: <你的主域名>  # 若你使用阿里云，亦可使用子域名如 internal.example.com
# 你用哪个填哪个
access_key_id: <阿里AK / DNSPod SecretId> 
access_key_secret: <阿里云SK / DNSPod SecretKey>
cloudflare_api_token: <Cloudflare Token>
```

## 开发规范指南
如果你想为项目做贡献，如添加新的 DNS 服务商支持，请遵循以下步骤：

1. **创建子类**：在 `./utils/provider` 目录下创建一个新的 Python 文件（如 `mydns.py`），并定义一个继承自 `BaseDns` 的类。
2. **实现方法**：实现 `BaseDns` 中的抽象方法，如 `create_client`、`get_dns_list`、`add_record` 和 `remove_record`。
3. **更新其他程序**：在 `./utils/__init__.py` 中使用 `from ... import ...` 导入你的新类。
4. **更新主程序**：在 `main.py` 中修改 `cls_map`，在 `from utils import list_node, BaseDns, ...` 后导入你的新类并添加到这个 dict 中。

有关新类的实现，请参考 `./utils/base.py` 和现有的 DNS 服务商实现。

另外请注意，本项目使用 `loguru` 进行日志记录，请在相关类中使用 `logger` 进行**适当的**日志输出，可参考现有实现。