# EcoMarket

基于 FastAPI + Vue3 + Qwen3.7-Plus 的智能校园二手交易平台。

让闲置流动起来，让交易更智能。

## 功能特性

- **用户系统**：注册登录、JWT 认证、信誉分评价
- **商品管理**：发布、搜索、分类筛选、收藏、卖家信息与信誉分展示
- **交易系统**：交易码确认机制 + 行锁防止超卖 + 多人并发请求
- **站内消息**：基于商品的买卖双方双向沟通，协商交易时间地点
- **AI 智能**：Qwen3.7-Plus 自动生成商品定价与描述
- **数据看板**：ECharts 可视化交易趋势、分类占比、价格分布
- **管理后台**：工作台统计、用户管理（禁用/启用/重置密码）、商品管理（上架/下架/删除）、分类 CRUD、交易监控、评价管理、消息管理
- **索引优化**：联合索引 + 覆盖索引 + FULLTEXT，查询性能提升 24 倍
- **双数据库**：MySQL 主库 + openGauss 备库自动降级
- **Redis 缓存**：首页缓存、统计看板、未读消息数，优雅降级

## 技术栈

| 层面 | 技术 |
|------|------|
| 后端 | FastAPI + SQLAlchemy 2.0 (异步) |
| 前端 | Vue3 + TypeScript + Element Plus + ECharts |
| 数据库 | MySQL 9.7 / openGauss |
| 缓存 | Redis 7 |
| AI | Qwen3.7-Plus (AsyncOpenAI) |
| 迁移 | Alembic |
| 测试 | pytest + pytest-asyncio |

## 快速开始

### 后端

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写数据库密码和 DASHSCOPE_API_KEY

# 3. 初始化数据
python scripts/init_data.py

# 4. 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

数据库策略通过 `.env` 中 `DB_STRATEGY` 配置：

| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `sqlite` | 使用 SQLite（`.env.example` 默认值） | 零配置开箱即用，适合快速体验 |
| `primary` | 仅使用 MySQL | 生产环境主库 |
| `fallback` | MySQL 主库，失败自动降级到 openGauss | 高可用生产环境 |
| `opengauss_only` | 仅使用 openGauss | 国产数据库演示 |

- `.env.example` 默认 `DB_STRATEGY=sqlite`，方便克隆后无需额外安装数据库即可运行
- 切换到 MySQL/openGauss 时，修改 `.env` 中 `DB_STRATEGY=fallback` 并填写对应的数据库连接信息
- 使用 MySQL 时可运行 `alembic upgrade head` 建表并应用索引优化

### 前端

```bash
cd frontend
npm install
npm run dev      # 开发模式 http://localhost:5173
npm run build    # 生产构建
```

### 测试

```bash
pytest tests/ -v
```

### Docker（可选）

```bash
docker-compose up -d   # 启动 MySQL + openGauss + Redis
```

## 交易流程

```
买家下单 → 卖家接受（生成 6 位交易码）→ 线下见面 → 买家输码确认收货 → 双方互评
```

- 下单时商品保持「在售」状态，允许多人同时发起请求
- 卖家接受后商品变「已预订」，其他请求自动拒绝
- 交易码仅卖家可见，线下交易时告知对方
- 买卖双方可通过站内消息协商交易时间地点

## API 文档

启动后端后访问：
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 测试账号

初始化数据后可用账号：
- 管理员: `admin / admin123`
- 学生: `王五 / test123456`

## 项目结构

```
EcoMarket/
├── app/                 # 后端（FastAPI）
│   ├── core/           # 配置、数据库、Redis、JWT
│   ├── models/         # 7 张表模型
│   ├── schemas/        # Pydantic 模型
│   ├── api/v1/         # 13 个路由模块
│   ├── services/       # 业务逻辑（事务、AI、搜索兼容）
│   └── utils/          # 工具函数
├── frontend/           # 前端（Vue3）
│   └── src/
│       ├── views/      # 10 个用户页面 + 7 个管理后台页面
│       ├── layouts/    # AdminLayout 管理后台布局
│       ├── components/ # 4 个组件（含 3 个 ECharts 图表）
│       ├── api/        # 11 个 API 模块
│       ├── stores/     # Pinia 状态管理
│       └── router/    # 路由 + 鉴权守卫 + 管理员守卫
├── alembic/            # 数据库迁移
├── tests/              # 单元测试
└── scripts/            # 种子数据、索引基准、压测脚本
```

详细文档见 [项目报告.md](项目报告.md)。

## License

MIT
