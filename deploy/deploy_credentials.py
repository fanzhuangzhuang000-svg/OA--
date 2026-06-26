#!/usr/bin/env python3
"""
安全凭据加载模块 - 从环境变量或 .env.deploy 文件读取敏感信息。

使用方式:
    from deploy_credentials import load_credentials, get_ssh_credentials_172, get_ssh_credentials_152

优先级: 环境变量 > .env.deploy 文件
"""
import os
import sys
from pathlib import Path


def _load_dotenv_file(filepath):
    """简易 .env 文件解析器，无需第三方依赖"""
    env_vars = {}
    p = Path(filepath)
    if not p.exists():
        return env_vars
    with open(p, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            if '=' not in line:
                continue
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip()
            # 去除引号
            if len(value) >= 2 and value[0] == value[-1] and value[0] in ('"', "'"):
                value = value[1:-1]
            env_vars[key] = value
    return env_vars


def load_credentials():
    """
    加载凭据。优先使用环境变量，其次读取 .env.deploy 文件。
    返回字典包含所有可能的凭据键。
    """
    # 1. 先尝试从 .env.deploy 文件加载
    deploy_dir = Path(__file__).parent.resolve()
    dotenv_path = deploy_dir / '.env.deploy'
    file_vars = _load_dotenv_file(dotenv_path)

    # 2. 以文件值为基底，环境变量覆盖
    result = {}
    all_keys = set(file_vars.keys()) | set(os.environ.keys())
    for key in all_keys:
        # 环境变量优先
        if key in os.environ and os.environ[key]:
            result[key] = os.environ[key]
        elif key in file_vars and file_vars[key]:
            result[key] = file_vars[key]
    return result


def _get_ssh_creds(prefix):
    """获取指定服务器的 SSH 凭据"""
    creds = load_credentials()
    host = creds.get(f'DEPLOY_HOST_{prefix}')
    user = creds.get(f'DEPLOY_USER_{prefix}')
    auth_method = creds.get('DEPLOY_AUTH_METHOD', 'key')
    ssh_key = creds.get('DEPLOY_SSH_KEY', '~/.ssh/id_rsa')
    password = creds.get(f'DEPLOY_PASSWORD_{prefix}')

    if not host or not user:
        print(f'错误: 缺少 DEPLOY_HOST_{prefix} 或 DEPLOY_USER_{prefix} 配置')
        print(f'请复制 .env.deploy.example 为 .env.deploy 并填入真实值')
        print(f'或设置环境变量 DEPLOY_HOST_{prefix} / DEPLOY_USER_{prefix}')
        sys.exit(1)

    return {
        'host': host,
        'port': int(creds.get(f'DEPLOY_PORT_{prefix}', 22)),
        'user': user,
        'auth_method': auth_method,
        'ssh_key': ssh_key,
        'password': password,
    }


def get_ssh_credentials_172():
    """获取 172 测试服务器凭据"""
    return _get_ssh_creds('172')


def get_ssh_credentials_152():
    """获取 152 展示服务器凭据"""
    return _get_ssh_creds('152')


def connect_ssh(creds):
    """
    根据凭据建立 SSH 连接。
    优先使用 SSH 密钥认证，密码仅作备选。
    """
    import paramiko
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    auth = creds['auth_method']
    key_path = os.path.expanduser(creds['ssh_key'])

    if auth == 'key' and Path(key_path).exists():
        ssh.connect(
            creds['host'],
            port=creds['port'],
            username=creds['user'],
            key_filename=key_path,
            timeout=10
        )
    elif creds.get('password'):
        ssh.connect(
            creds['host'],
            port=creds['port'],
            username=creds['user'],
            password=creds['password'],
            timeout=10
        )
    else:
        print('错误: 无法建立 SSH 连接')
        print(f'认证方式: {auth}')
        print(f'密钥路径: {key_path} (存在: {Path(key_path).exists()})')
        print('请确保 SSH 密钥存在，或在 .env.deploy 中设置 DEPLOY_PASSWORD')
        sys.exit(1)

    return ssh
