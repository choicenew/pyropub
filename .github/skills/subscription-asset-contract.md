# VehereGo Subscription Asset Contract Specification (订阅资源统一契约规范)

## 1. 核心设计原则
本规范定义 VehereGo 双端 (构建端 CI `aura-wallpaper` 与 消费端 Flutter App `veherego`) 统一遵循的 JSON 数据契约标头。所有资源包根节点必须包含强类型 `type` 标头，实现 100% 确定性解析。

---

## 2. 强类型 `type` 标头枚举定义

| 领域类型枚举 (`SubscriptionType`) | 契约代号 (`code`) | 包含根节点核心字段 | 资源路径示例 |
| :--- | :--- | :--- | :--- |
| `appRules` | `"rules"` | `"rules": [...]` | `veherego_assets/rules/default_rules_zh.json` |
| `smartDictionary` | `"dictionary"` | `"smart_rules": [...]` | `veherego_assets/dictionaries/liveupdate_dictionary_zh.json` |
| `brandCatalog` | `"brands"` | `"brand_aliases": {...}` | `veherego_assets/brands/brands_manifest.json` |
| `travelRules` | `"travel"` | `"transit_types": {...}` | `veherego_assets/travel/travel_rules_zh.json` |
| `identityRules` | `"identity"` | `"identity_cards": [...]` | `veherego_assets/identity/identity_manifest.json` |
| `storeCatalog` | `"store"` | `"sources": [...]` | `veherego_assets/store_manifest.json` |

---

## 3. 标准 Root Header 样例

```json
{
  "type": "rules",
  "version": 1,
  "description": "VehereGo Standard App Rules",
  "updated_at": "2026-10-23T00:00:00Z",
  "locale": "zh",
  "region": "CN",
  "rules": []
}
```

所有的 JSON 文件无论在 Assets 目录或 CI 构建库中，均严格以此为唯一权威契约。
