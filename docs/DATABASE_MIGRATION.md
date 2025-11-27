# 数据库迁移指南

本项目使用 Alembic 进行数据库版本管理和迁移。

## 快速开始

### 1. 初始化数据库（首次使用）

```bash
# 进入后端目录
cd backend

# 运行迁移
alembic upgrade head
```

这将创建所有必需的表：
- `users` - 用户表
- `conversations` - 对话表
- `messages` - 消息表

### 2. 查看当前迁移状态

```bash
alembic current
```

### 3. 查看迁移历史

```bash
alembic history
```

## 数据库结构

### users 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| email | String(255) | 邮箱（唯一） |
| hashed_password | String(255) | 哈希后的密码 |
| is_active | Boolean | 是否激活 |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### conversations 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | String(36) | 主键（UUID） |
| user_id | Integer | 外键 → users.id |
| title | String(255) | 对话标题（可选） |
| created_at | DateTime | 创建时间 |
| updated_at | DateTime | 更新时间 |

### messages 表
| 字段 | 类型 | 说明 |
|------|------|------|
| id | Integer | 主键 |
| conversation_id | String(36) | 外键 → conversations.id |
| role | String(20) | 角色（user/assistant/system） |
| content | Text | 消息内容 |
| timestamp | DateTime | 时间戳 |

## 创建新迁移

### 自动生成迁移（推荐）

当你修改了模型后，可以自动生成迁移：

```bash
alembic revision --autogenerate -m "描述你的更改"
```

### 手动创建迁移

```bash
alembic revision -m "描述你的更改"
```

然后编辑生成的文件（在 `alembic/versions/` 目录下）。

## 迁移操作

### 升级到最新版本

```bash
alembic upgrade head
```

### 升级到特定版本

```bash
alembic upgrade <revision_id>
```

### 降级一个版本

```bash
alembic downgrade -1
```

### 降级到特定版本

```bash
alembic downgrade <revision_id>
```

### 降级到初始状态

```bash
alembic downgrade base
```

## 重置数据库

如果需要完全重置数据库：

```bash
# 删除数据库文件
rm data/kimitalk.db

# 重新运行迁移
alembic upgrade head
```

## 生产环境注意事项

1. **备份数据库**：在运行迁移前务必备份
   ```bash
   cp data/kimitalk.db data/kimitalk.db.backup
   ```

2. **测试迁移**：先在测试环境验证迁移
   ```bash
   # 在测试环境运行
   alembic upgrade head
   
   # 验证数据
   # 如果有问题，可以回滚
   alembic downgrade -1
   ```

3. **迁移顺序**：按照版本号顺序执行

4. **避免数据丢失**：
   - 删除列时先确认数据已迁移
   - 修改列类型时注意兼容性
   - 添加非空列时提供默认值

## 故障排查

### 问题：迁移失败

```bash
# 查看详细错误
alembic upgrade head --sql

# 手动检查 SQL
```

### 问题：数据库状态不一致

```bash
# 标记当前版本为特定版本（不执行 SQL）
alembic stamp head
```

### 问题：需要回滚

```bash
# 回滚最近的迁移
alembic downgrade -1

# 查看会执行的 SQL（不实际执行）
alembic downgrade -1 --sql
```

## 常用命令速查

| 命令 | 说明 |
|------|------|
| `alembic current` | 查看当前版本 |
| `alembic history` | 查看迁移历史 |
| `alembic upgrade head` | 升级到最新 |
| `alembic downgrade -1` | 回滚一个版本 |
| `alembic revision -m "msg"` | 创建新迁移 |
| `alembic revision --autogenerate -m "msg"` | 自动生成迁移 |
| `alembic stamp head` | 标记版本（不执行 SQL） |

## 配置文件

- `alembic.ini` - Alembic 配置文件
- `alembic/env.py` - 环境配置
- `alembic/script.py.mako` - 迁移模板
- `alembic/versions/` - 迁移脚本目录
