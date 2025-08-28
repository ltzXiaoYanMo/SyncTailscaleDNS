# SyncTailscaleDNS
[![State-of-the-art Shitcode](http://img.shields.io/static/v1?label=State-of-the-art&message=Shitcode&color=7B5804)](https://github.com/trekhleb/state-of-the-art-shitcode) <-- 本项目是一个纯正的 shitcode

## 项目简介
SyncTailscaleDNS 用于自动将 Tailscale 网络中的节点 IP（A/AAAA 记录）同步到公网 DNS（如阿里云 DNS、Cloudflare DNS）。适合需要将 Tailscale 内网主机自动暴露到公网 DNS 的场景。

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

## 配置说明（config.yaml 示例）
```yaml
dns_provider: alidns # 可选： alidns / cloudflare
zone_id: <你的DNS区域ID>  # 若你使用 Cloudflare，否则留空
domain_name: <你的主域名>  # 若你使用阿里云，亦可使用子域名如 internal.example.com
# 你用哪个填哪个
access_key_id: <阿里云AK> 
access_key_secret: <阿里云SK>
cloudflare_api_token: <Cloudflare Token>
```
