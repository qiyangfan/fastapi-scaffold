# GATES — 门禁矩阵、触发条件与负向验收

本仓是复制型种子：门禁按"实际具备的形态面"配置。新增形态时按下表触发器补门禁，
不要预装无法真跑的检查（纸面门禁）。

## 本地 / CI 对应

```bash
make setup   # 安装依赖 + pre-commit hooks
make gates   # ruff + format + mypy + pylint + import-linter + deptry + vulture + secrets + docs + infra + pytest
make audit   # pip-audit（需要 registry，CI security.yml 同款）
```

CI 分三份：`ci.yml`（质量）、`security.yml`（密钥/依赖漏洞/SBOM/workflow lint）、
`codeql.yml`（SAST）。

| 门禁 | 命令 | 本地 | CI | 负向验收（2026-11-21） |
|---|---|---|---|---|
| Ruff（全规则族 + C901/PLR/PERF/TRY/BLE/DTZ/G/LOG/T20/PTH/ICN） | `make lint` | ✅ | ci.yml | ✅ `print()`（T20）→ 红 |
| Ruff format | `make format-check` | ✅ | ci.yml | ✅ 未格式化函数 → 红 |
| mypy strict | `make typecheck` | ✅ | ci.yml | ✅ 类型不匹配 → 红 |
| pylint（体积/返回数/循环 import/E） | `make pylint` | ✅ | ci.yml | ✅ 语法错误 → 红 |
| 架构（import-linter 2 契约） | `make imports` | ✅ | ci.yml | ✅ api→main 反向依赖 → 红 |
| 依赖卫生（deptry） | `make deps` | ✅ | ci.yml | ✅ 未声明的 `yaml` → 红 |
| 死代码（vulture，100%） | `make dead` | ✅ | ci.yml | ✅ return 后不可达代码 → 红（100% 档只覆盖不可达代码，见下方说明） |
| 覆盖率（行+分支，≥70） | `make test` | ✅ | ci.yml | ✅ 强制 100% → 红 |
| 许可证 allowlist（仅生产依赖） | `make licenses` | ✅ | ci.yml | ✅ 注入 GPL-3.0 假包 → 红 |
| 密钥（gitleaks） | `gitleaks dir .` / `detect` 全历史 | ✅ | security.yml | ✅ 植入假 AKIA 凭据 → 红 |
| 依赖漏洞 | `pip-audit --local` | ✅ | security.yml | 正向通过；负向需引入漏洞版本，建远端后 CI 实证 |
| SBOM | `syft dir:. -c .syft.yaml` | - | security.yml（artifact） | 正向生成在 CI 执行 |
| 提交信息 | `scripts/commitcheck.sh --file` | ✅ pre-commit | - | ✅ 非法标题 → 红 |
| Workflow lint | `actionlint` | ✅ | security.yml | ✅ 非法 YAML → 红 |
| YAML lint | `yamllint` | ✅ | security.yml | ✅ 与 actionlint 同文件 |
| Markdown lint | `markdownlint-cli2` | ✅ | ci.yml | ✅ 跳级标题（MD001）→ 红 |
| Dockerfile lint | `hadolint Dockerfile` | ✅ | -（镜像构建时） | ✅ 未固定 apt 版本 → 红 |
| SAST（CodeQL） | workflow | - | codeql.yml | 需远端仓库，建仓后首次运行实证 |

## 说明

- vulture 取 `--min-confidence 100`（与 siku 同口径）：稳定命中的是不可达代码；
  未使用函数/变量置信度低于 100，需要更激进清理时另立 change 下调并逐条裁决。
- import-linter 的契约从第一天起就是可执行的（`api` 不得依赖 `app.main`，
  `settings` 是叶子）；新增领域层时按层追加 contract，不要堆成通配。

## 触发矩阵（新增形态时补）

| 新增形态 | 必须补的门禁 |
|---|---|
| SQLAlchemy + Alembic | 空库迁移演练、迁移单头断言、降级→升级 roundtrip、迁移约定测试（禁 ENUM/数值状态/无时区时间戳） |
| OpenAPI 契约 | 重生成后 `git diff --exit-code` + oasdiff |
| 鉴权/租户 | 分域覆盖率地板（安全域单列）、越权负向用例 |
| 前端页面 | Playwright + axe（serious/critical）、bundle size 预算 |
| MCP/外部服务 | 契约测试 + 超时/重试/降级测试 |
| 发布镜像 | trivy image（HIGH/CRITICAL，`--ignore-unfixed`）+ 基础镜像钉 sha256 |

## 平台侧（建 GitHub 远端后）

- 分支保护：`secrets`、`deps`、`sbom`、`workflows`、`codeql`、`quality` 设为 required。
- 必须按首跑展开后的真实 job 名设置，禁止猜名字。
- CodeQL 首次运行后再设 required；私库免费版不支持分支保护时，如实记录为纸面状态。

## 抑制纪律

- 无行内 `noqa`；全局 ignore（`TRY003`、`RUF001-3`）与 `tests/*` 的 `S101`
  是规则集取舍，不是对具体缺陷的豁免。
- vulture 取 100% 档，只稳定命中不可达代码；下调置信度需要单独裁决。
- 新增抑制必须写原因、负责人、到期日；到期未复审即视为门禁失效。
