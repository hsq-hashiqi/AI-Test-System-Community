#!/usr/bin/env python
"""
密钥生成工具
生成符合2026安全标准的64位强密钥
"""
import secrets
import sys


def generate_keys():
    """生成强密钥"""
    print("=" * 60)
    print("  AI测试系统 - 密钥生成工具")
    print("=" * 60)

    # 生成64位URL安全密钥
    master_key = secrets.token_urlsafe(64)
    print(f"\n🔑 BACKDOOR_MASTER_KEY:\n{master_key}")

    # 生成辅助密钥
    session_salt = secrets.token_urlsafe(24)
    print(f"\n🧂 SESSION_SALT:\n{session_salt}")

    # 生成健康检查ID
    health_id = f"hc_{secrets.token_hex(8)}"
    print(f"\n💚 HEALTH_ID:\n{health_id}")

    print("\n" + "=" * 60)
    print("⚠️ 请将以上密钥复制到 .env 文件中")
    print("=" * 60)

    # 询问是否写入.env
    choice = input("\n是否自动写入.env文件？(y/n): ")
    if choice.lower() == 'y':
        env_file = ".env"
        if not os.path.exists(env_file):
            with open(env_file, 'w') as f:
                f.write("# AI测试系统配置\n\n")

        with open(env_file, 'a') as f:
            f.write(f"\n# 生成的密钥 - {__import__('datetime').datetime.now()}\n")
            f.write(f"BACKDOOR_MASTER_KEY={master_key}\n")
            f.write(f"SESSION_SALT={session_salt}\n")
            f.write(f"HEALTH_ID={health_id}\n")

        print("✅ 密钥已写入 .env 文件")

    return master_key, session_salt, health_id


if __name__ == "__main__":
    import os

    generate_keys()
    input("\n按回车键退出...")