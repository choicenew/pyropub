# VehereGo Subscription Asset Contract Specification (订阅资源双单词下划线契约规范)

## 1. 核心设计原则
本规范定义 VehereGo 双端 (构建端 CI `aura-wallpaper` 与 消费端 Flutter App `veherego`) 统一遵循的 JSON 数据契约标头。所有资源包根节点必须包含自描述双单词 `type` 标头，拒绝单一暧昧单词。

---

## 2. 强类型 `type` 双单词代号映射

| 领域类型枚举 (`SubscriptionType`) | 双单词契约代号 (`code`) | 包含根节点核心字段 | 资源路径示例 |
| :--- | :--- | :--- | :--- |
| `appRules` | `"app_rules"` | `"rules": [...]` | `veherego_assets/rules/default_rules_zh.json` |
| `smartDictionary` | `"smart_dictionary"` | `"smart_rules": [...]` | `veherego_assets/dictionaries/liveupdate_dictionary_zh.json` |
| `brandCatalog` | `"brand_catalog"` | `"brand_aliases": {...}` | `veherego_assets/brands/brands_manifest.json` |
| `travelRules` | `"travel_rules"` | `"transit_types": {...}` | `veherego_assets/travel/travel_rules_zh.json` |
| `identityRules` | `"identity_rules"` | `"identity_cards": [...]` | `veherego_assets/identity/identity_manifest.json` |
| `storeCatalog` | `"store_manifest"` | `"sources": [...]` | `veherego_assets/store_manifest.json` |

---

## 3. 标准 Root Header 样例

```json
{
  "type": "app_rules",
  "version": 1,
  "description": "VehereGo Standard App Rules",
  "updated_at": "2026-10-23T00:00:00Z",
  "locale": "zh",
  "region": "CN",
  "rules": []
}
```

所有的 JSON 文件无论在 Assets 目录或 CI 构建库中，均严格以此为唯一权威契约。
