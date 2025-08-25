import subprocess
import json
import re
import logging

logger = logging.getLogger(__name__)

# 编译一次正则表达式，提升性能
DNS_NAME_PATTERN = re.compile(r"\.kudu-major\.ts\.net\.?$")


def _extract_device_info(device_data):
    """提取单个设备的信息"""
    dns_name = device_data.get("DNSName", "")
    hostname = DNS_NAME_PATTERN.sub("", dns_name) if dns_name else "N/A"

    tailscale_ips = device_data.get("TailscaleIPs", [])
    ipv4_addresses = [ip for ip in tailscale_ips if ":" not in ip]
    ipv6_addresses = [ip for ip in tailscale_ips if ":" in ip]

    return {
        "hostname": hostname,
        "ipv4_addresses": ipv4_addresses or ["N/A"],
        "ipv6_addresses": ipv6_addresses or ["N/A"],
    }


def _execute_tailscale_command():
    """执行 tailscale status 命令并返回结果"""
    try:
        command = subprocess.run(
            ["tailscale", "status", "--json"],
            capture_output=True,
            encoding="utf-8",
            check=True,
        )
        return command
    except subprocess.CalledProcessError as err:
        logger.error("Command execution failed: %s", err)
        if err.stderr:
            logger.error("Error output: %s", err.stderr)
        return None
    except Exception as err:
        logger.error("Unexpected error: %s", err)
        return None


def _parse_tailscale_data(stdout):
    """解析 tailscale 命令输出的 JSON 数据"""
    try:
        data = json.loads(stdout)
        return data
    except json.JSONDecodeError as e:
        logger.error("Invalid JSON output: %s", stdout)
        logger.error("JSON decode error: %s", e)
        return None


def _build_result_data(data):
    """根据解析的数据构建结果数据结构"""
    result = {"devices": [], "total": 0}

    # 添加本机信息
    self_info = data.get("Self", {})
    if self_info:
        device_info = _extract_device_info(self_info)
        result["devices"].append(device_info)

    # 添加对等设备信息
    peer_info = data.get("Peer", {})
    if isinstance(peer_info, dict):
        for peer_data in peer_info.values():
            device_info = _extract_device_info(peer_data)
            result["devices"].append(device_info)
    else:
        logger.warning("Peer data is not a dictionary: %s", type(peer_info))

    # 添加设备总数
    result["total"] = len(result["devices"])
    return result


def list_node(config_data=None):
    # 执行命令
    command = _execute_tailscale_command()
    if command is None:
        return None

    # 检查命令输出
    if not command.stdout:
        logger.error("No output from tailscale command")
        return None

    # 解析数据并构建结果
    data = _parse_tailscale_data(command.stdout)
    if data is None:
        return None
    result = _build_result_data(data)

    # 返回结果
    return result
