# Render API Skill

[English](#english) | [中文](#中文)

---

## English

A Claude Code skill for managing Render cloud platform via API. Zero dependencies, works with Free Plan.

### Features

- **Zero Dependencies**: Bash (curl only), Python (stdlib only)
- **Free Plan Compatible**: All core operations work with free API keys
- **Multi-Account Support**: Manage multiple Render accounts via config
- **Batch Operations**: Run commands across all profiles

### Installation

```bash
# Personal skills
cp -r render-skills ~/.claude/skills/

# Or project skills
cp -r render-skills .claude/skills/
```

### Configuration

Create `config.json` from template:

```json
{
  "mode": "json",
  "default_profile": "default",
  "profiles": {
    "default": { "api_key": "rnd_YOUR_KEY" },
    "company": { "api_key": "rnd_OTHER_KEY" }
  }
}
```

Or use environment variables (`mode: "env"`):
```bash
export RENDER_API_KEY="rnd_xxx"
# Multiple: export RENDER_API_KEYS="rnd_xxx,rnd_yyy"
```

Get API key: https://dashboard.render.com/u/settings#api-keys

### Usage

**CLI Scripts:**
```bash
./scripts/render-api.sh services list
./scripts/render-api.sh deploys trigger srv-xxx
./scripts/render-api.sh batch services

python scripts/render_client.py services
python scripts/render_client.py batch workspaces
```

**Direct curl:**
```bash
curl -s "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### Free Plan Limitations

| Feature | Free | Paid |
|---------|------|------|
| Deploy/Restart/Suspend | ✓ | ✓ |
| Postgres | ✓ (30-day) | ✓ |
| Key Value | ✓ (ephemeral) | ✓ |
| Custom domains | 2 max | Unlimited |
| Horizontal autoscaling | ✗ | ✓ |

### Files

- `SKILL.md` - Main skill file
- `API-REFERENCE.md` - Full endpoint documentation
- `EXAMPLES.md` - Workflow examples
- `scripts/render-api.sh` - Bash CLI
- `scripts/render_client.py` - Python client

---

## 中文

用于通过apikey 管理 Render 云平台的 Claude Code skills。零依赖，支持免费计划。

### 特性

- **零依赖**: Bash（仅需 curl）、Python（仅用标准库）
- **免费计划兼容**: 所有核心操作均可使用免费 API key
- **多账户支持**: 通过配置文件管理多个 Render 账户
- **批量操作**: 跨所有配置文件执行命令

### 安装

```bash
# 个人技能
cp -r render-skills ~/.claude/skills/

# 或项目技能
cp -r render-skills .claude/skills/
```

### 配置

从模板创建 `config.json`：

```json
{
  "mode": "json",
  "default_profile": "default",
  "profiles": {
    "default": { "api_key": "rnd_YOUR_KEY" },
    "company": { "api_key": "rnd_OTHER_KEY" }
  }
}
```

或使用环境变量（`mode: "env"`）：
```bash
export RENDER_API_KEY="rnd_xxx"
# 多个: export RENDER_API_KEYS="rnd_xxx,rnd_yyy"
```

获取 API key: https://dashboard.render.com/u/settings#api-keys

### 使用方法

**CLI 脚本：**
```bash
./scripts/render-api.sh services list
./scripts/render-api.sh deploys trigger srv-xxx
./scripts/render-api.sh batch services

python scripts/render_client.py services
python scripts/render_client.py batch workspaces
```

**直接 curl：**
```bash
curl -s "https://api.render.com/v1/services" \
  -H "Authorization: Bearer $RENDER_API_KEY"
```

### 免费计划限制

| 功能 | 免费 | 付费 |
|------|------|------|
| 部署/重启/暂停 | ✓ | ✓ |
| Postgres | ✓ (30天) | ✓ |
| Key Value | ✓ (临时) | ✓ |
| 自定义域名 | 最多2个 | 无限 |
| 水平自动扩展 | ✗ | ✓ |

### 文件说明

- `SKILL.md` - 主技能文件
- `API-REFERENCE.md` - 完整端点文档
- `EXAMPLES.md` - 工作流示例
- `scripts/render-api.sh` - Bash CLI
- `scripts/render_client.py` - Python 客户端

---

## License

MIT
