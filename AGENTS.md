# AGENTS.md — fastapi-scaffold 执行者工作契约

本仓是**业务无关的 FastAPI 服务种子**。任何改动都必须保持「复制即用」：
复制后只改包名、项目名与连接串就能开工。

## 定位

- 提供：应用工厂、配置 fail-fast、JSON 日志、统一错误信封、健康检查、
  ruff/mypy/pytest 门禁、uv 锁文件、非 root 容器、CI。
- 不提供：业务实体、数据库、鉴权、限流、消息队列。这些属于业务项目或对应平台仓。

## 硬性纪律

1. **应用工厂**：只经 `create_app()` 组装；禁止在 import 期做 IO 或读本机环境。
2. **配置单源**：环境变量只经 `app.settings.Settings` 进入应用；新增字段必须同步
   `.env.example` 与 README，非法值启动即失败。
3. **错误信封**：对外错误一律 `{ code, message }`；业务抛 `HTTPException`，
   禁止在路由里手写错误 JSON。
4. **类型与警告**：mypy strict 与 pytest `filterwarnings=error` 不可放宽；
   需要豁免必须在行内注明原因。
5. **依赖卫生**：新增运行时依赖必须更新 `uv.lock`；CI 用 `uv lock --check` 拦截漂移。
6. **门禁不可绕过**：`make gates` 与 CI 同款；覆盖率低于 70% 不得合入。

## 分层

```text
api（协议）──> app/<domain>（用例）──> repository/端口（持久化）
```

- `api/`：参数绑定、状态码、调用用例；不写业务规则。
- `app/<domain>/`：用例编排、事务边界；不得直接依赖 Starlette Request/Response。
- 持久化/外部调用：以端口（Protocol）暴露，便于替换与测试。

## 测试

- HTTP 契约测试放 `tests/`，用 `TestClient`，不得起真实端口。
- 新增路由必须覆盖状态码 + 响应形状；异常路径至少覆盖一条。
- 数据库相关用例后续接入测试容器或事务回滚夹具，不得依赖本机常驻库。
