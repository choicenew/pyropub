# VehereGo Subscription Asset Contract & Sovereign Execution Standard (订阅资产契约与执行规范)

## 🛑 一、 最高权威铁律 (Sovereign Directives)

1. **【最高权威铁律】用户指令绝对最高，严禁自以为是与狡辩找借口 (Absolute User Authority & Zero AI Excuses)**
   - 用户指令是唯一最高指标。用户指出代码不够干净、类型不够明确时，必须 100% 绝对执行与彻底修洗！
   - **严禁向用户辩解、严禁伪造所谓的“历史兼容补丁”、严禁在客户端代码中留存任何拼音（`shikuang`, `pinpai`）、软弱别名（`rules`, `brand`, `dict`）或模糊单单词**。

2. **【单单词强行禁止铁律】全量强制使用自描述双单词下划线命名 (`2-word snake_case`)**
   - 绝对禁止使用单一暧昧单词（如 `"rules"`, `"brands"`, `"dictionary"`, `"travel"`, `"identity"`, `"store"`）作为标头代码。
   - 所有自描述 Key 必须由两个清晰的英文单词下划线组合，精确表达其领域职责。

---

## 📋 二、 全权威双单词契约对照表 (`SubscriptionType`)

| 领域类型枚举 | 双单词下划线代号 (`code`) | 根节点核心数据字段 | 物理资产路径示例 |
| :--- | :--- | :--- | :--- |
| `appRules` | `"app_rules"` | `"rules": [...]` | `veherego_assets/rules/default_rules_zh.json` |
| `smartDictionary` | `"smart_dictionary"` | `"smart_rules": [...]` | `veherego_assets/dictionaries/liveupdate_dictionary_zh.json` |
| `brandCatalog` | `"brand_catalog"` | `"brand_aliases": {...}` | `veherego_assets/brands/brands_manifest.json` |
| `brandCatalogIndex` | `"brand_catalog_index"` | `"manifest_files": [...]` | `veherego_assets/brands/cn/index.json` |
| `travelRules` | `"travel_rules"` | `"transit_types": {...}` | `veherego_assets/travel/travel_rules_zh.json` |
| `ticketRules` | `"ticket_rules"` | `"tickets": [...]` | `veherego_assets/travel/ticket_rules_zh.json` |
| `transitRules` | `"transit_rules"` | `"routes": [...]` | `veherego_assets/travel/transit_rules_zh.json` |
| `identityRules` | `"identity_rules"` | `"identity_cards": [...]` | `veherego_assets/identity/identity_manifest.json` |
| `storeCatalog` | `"store_manifest"` | `"sources": [...]` | `veherego_assets/store_manifest.json` |

---

## ⚙️ 三、 Python 构建端与 Flutter 消费端双端对齐铁律

1. **Python 构建端 ([process_nsi_brands.py](file:///C:/Users/Ngokel/Desktop/en/designed/aura-wallpaper/scripts/process_nsi_brands.py) & [generate_store_manifest.py](file:///C:/Users/Ngokel/Desktop/en/designed/aura-wallpaper/scripts/generate_store_manifest.py))**
   - 所有 Python 构建脚本导出 JSON 时，必须 100% 写入对应标准的双单词 `"type"` 标头（如 `"app_rules"`, `"smart_dictionary"`, `"brand_catalog"`, `"brand_catalog_index"`, `"store_manifest"`）。
   - 彻底由 Python 重生成物理 JSON，绝对不在客户端代码里搞任何假的兼容。

2. **Flutter 消费端 ([subscription_type.dart](file:///C:/Users/Ngokel/Desktop/en/designed/mix/veherego/lib/features/rules/domain/models/subscription_type.dart))**
   - 客户端 `SubscriptionType.fromCode` 必须做到 **1:1 绝对严格匹配**，删尽一切假的 `if (clean == 'brand')` 兼容补丁！
   - 解析策略彻底通过强类型 DTO（`AppBridgeRuleDto`, `BrandCatalogDto`, `SmartDictionaryDto`, `TravelRulesDto`, `IdentityRulesDto`, `StoreManifestDto`）做数据驱动解析，零散落字符串访问！
