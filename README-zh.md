# auto-ssl-qcloud

Let's Encrypt 自动签发 SSL 证书 + 腾讯云 SSL 证书上传。

自动化完整的 SSL 证书生命周期管理：
- **签发/续期** 证书，基于 [acme.sh](https://github.com/acmesh-official/acme.sh) 的 DNS-01 验证（腾讯云 DNS）
- **上传** 证书到腾讯云 SSL 证书服务

## 前置条件

- Python 3.10+
- [acme.sh](https://github.com/acmesh-official/acme.sh) 已安装（`~/.acme.sh/acme.sh`）
- 腾讯云账号及 API 密钥

## 快速开始

```bash
# 1. 克隆并安装依赖
git clone https://github.com/huchi996/auto-ssl-qcloud-skills.git
cd auto-ssl-qcloud-skills
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# 2. 配置密钥
cp .env.example .env
# 编辑 .env，填入腾讯云 API 密钥：
#   COS_SECRET_ID=你的 SecretId
#   COS_SECRET_KEY=你的 SecretKey

# 3. 确保 acme.sh 已配置腾讯云 DNS API
export Tencent_SecretId="你的 SecretId"
export Tencent_SecretKey="你的 SecretKey"
```

## 使用方法

```bash
source .venv/bin/activate

# 签发新证书
python auto_ssl.py issue example.com

# 续期证书（已签发过会自动续期）
python auto_ssl.py issue example.com

# 上传证书到腾讯云 SSL
python auto_ssl.py upload example.com

# 签发 + 上传一步完成
python auto_ssl.py issue-and-upload example.com

# 查看本地已管理的所有证书
python auto_ssl.py list
```

## Claude Code 集成

本项目内置 Claude Code skill（`.claude/skills/auto-ssl-qcloud/SKILL.md`）。在此项目中使用 Claude Code 时，Claude 可以直接帮你管理 SSL 证书——只需用自然语言描述需求即可。

## 配置项

环境变量（在 `.env` 中设置）：

| 变量 | 必填 | 默认值 | 说明 |
|---|---|---|---|
| `COS_SECRET_ID` | 是 | - | 腾讯云 API SecretId |
| `COS_SECRET_KEY` | 是 | - | 腾讯云 API SecretKey |
| `DNS_API` | 否 | `dns_tencent` | acme.sh 使用的 DNS 提供商 |

## 工作原理

```
acme.sh --issue --dns dns_tencent  -->  ~/.acme.sh/<domain>_ecc/*.cer + *.key
                                              |
                                              v
                                    腾讯云 SSL UploadCertificate API
                                              |
                                              v
                                    证书可在腾讯云控制台查看和管理
```

## 许可证

MIT
