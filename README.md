# fastapi-scaffold · Python 服务脚手架

FastAPI 服务的最小可运行骨架：复制、改包名、加业务子包即开工。
与 kongming 的工具链习惯一致（uv / ruff / mypy / pytest），但不含数据库、鉴权与业务域。

## 技术栈

| 组件 | 版本 | 说明 |
| --- | --- | --- |
| Python | 3.13（mise 锚定） | `requires-python >= 3.13` |
| uv | 0.13 | 锁文件冻结安装，`uv.lock` 入库 |
| FastAPI | 0.143+ | ASGI 服务 |
| pydantic-settings | 2.x | 环境变量契约，启动期 fail-fast |
| ruff / mypy / pytest | 最新 | lint + 格式 + strict 类型 + 覆盖率门禁 |

## 快速开始

```bash
mise install
make setup               # 安装依赖 + pre-commit hooks
cp .env.example .env
make run                 # http://127.0.0.1:3000
curl -s 127.0.0.1:3000/health/live
curl -s 127.0.0.1:3000/health/ready
```

环境变量：`APP_ENV`（development|production|test）、`PORT`、`LOG_LEVEL`
（DEBUG|INFO|WARNING|ERROR）。非法值由 pydantic-settings 在启动期拒绝。

## 门禁

```bash
make setup   # 安装依赖 + pre-commit hooks
make gates   # ruff + format + mypy + pylint + import-linter + deptry + vulture + 许可证 + secrets + docs + infra + pytest
make audit   # pip-audit（需要 registry，CI security.yml 同款）
```

CI 分三份：`ci.yml`（质量）、`security.yml`（密钥/依赖漏洞/SBOM/workflow lint）、
`codeql.yml`（SAST）。完整门禁矩阵、触发条件与负向验收证据见 [GATES.md](GATES.md)。

## 目录

```text
src/app/
├── main.py           # create_app 工厂：日志、错误处理器、路由挂载
├── settings.py       # 环境变量契约（pydantic-settings）
├── logging.py        # 单行 JSON 日志
├── errors.py         # 统一错误信封 { code, message }
└── api/health.py     # /health/live、/health/ready
tests/                # HTTP 契约测试（TestClient）
```

## 约定

- **应用工厂**：只通过 `create_app()` 组装；测试注入 `Settings`，不读本机环境。
- **错误信封**：业务代码只抛 `HTTPException`；未捕获异常统一 500 + `INTERNAL_ERROR`，
  且必须打日志。
- **健康检查**：`live` 只看进程；`ready` 在接入数据库/缓存后聚合依赖探测，全绿才 200。
- **日志**：JSON 单行；生产不打印堆栈以外的敏感字段。
- **依赖**：新增运行时依赖必须同步 `uv.lock`；`uv.lock --check` 在 CI 执法。
- **分层**：`api/` 只做协议转换，业务用例放 `app/<domain>/`；`api` 不得直接写 SQL。

## 新建业务项目

```bash
cp -R ~/workspace/templates/fastapi-scaffold ~/workspace/<新项目>
cd ~/workspace/<新项目>
rm -rf .git && git init
# 改 pyproject 的 project.name、容器名与 .env
# 包名 app 建议保留；若必须改名，需同步 [tool.importlinter]、mypy/deptry/coverage
# 配置与全部 import（许可证脚本会自动读取新项目名，无需改脚本）
```

按需扩展（本种子刻意不预置）：SQLAlchemy + Alembic、鉴权、限流、Prometheus 指标、
MCP 适配层。数据库接入后把 ready 探针改为真实连接探测。
