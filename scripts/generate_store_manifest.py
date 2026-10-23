import os
import json
import glob

WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VEHEREGO_ASSETS_DIR = os.path.join(WORKSPACE, 'veherego_assets')
CONFIGS_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'configs')
BRANDS_OUT_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'brands')

# 使用全球高速 jsDelivr CDN 作为默认 CDN，支持环境变量覆盖
CDN_BASE_URL = os.environ.get('CDN_BASE_URL', 'https://cdn.jsdelivr.net/gh/choicenew/pyropub@main/veherego_assets')

def load_json_config(file_name, default_val):
    config_path = os.path.join(CONFIGS_DIR, file_name)
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Warning: Failed to load config {file_name}: {e}")
    return default_val

COUNTRY_LANGS_CONFIG = load_json_config('country_languages.json', {})
CATEGORIES_CONFIG = load_json_config('categories_config.json', {})
THIRD_PARTY_CONFIG = load_json_config('third_party_sources.json', {})

DEFAULT_FALLBACK_LANG = COUNTRY_LANGS_CONFIG.get('default_fallback_lang', 'en')
COUNTRIES_MAP = COUNTRY_LANGS_CONFIG.get('countries', {})

OFFICIAL_TITLE_TEMPLATES = {
    "rules": {
        "cn": ("中国区 - 常用 App 专属提取规则包", "China App Extraction Rules", "针对菜鸟、美团、顺丰、12306 等中国区高频 App 的专属提取规则"),
        "us": ("US App Extraction Rules", "US App Extraction Rules", "Rules for DoorDash, UberEats, FedEx, UPS, and Amazon"),
        "001": ("Official Global App Extraction Rules", "Official Global App Extraction Rules", "Global parcel, food delivery, and travel extraction rules")
    },
    "dictionary": {
        "cn": ("中文多语言状态推导词典", "Chinese Status Dictionary", "精炼中文包裹、餐饮、打车与出票全流程推导信号词典"),
        "us": ("English Smart Status Dictionary", "English Smart Status Dictionary", "English logistics, delivery, and ticketing status dictionary"),
        "jp": ("日本宅急便与便利店状态推断词典", "Japanese Status Dictionary", "日文便利店自提、宅急便与餐饮状态推导词典"),
        "ko": ("Korean Smart Status Dictionary", "Korean Status Dictionary", "韩文配送、快递与外卖状态推导词典")
    },
    "travel": {
        "cn": ("中国区 - 12306 高铁/民航/客运出行规则", "China Rail & Flight Travel Rules", "包含铁路 12306、中国民航登机牌与城际巴士检票口推导规则"),
        "us": ("International Flight & Rail Travel Rules", "International Travel Rules", "Includes Amtrak, Eurostar, Delta, and United Airlines travel rules"),
        "jp": ("日本交通・新幹線・航空チケット規則", "Japan Transit Travel Rules", "JR新幹線、日本航空、全日空の交通チケット規則"),
        "ko": ("Korean Transit & Airline Travel Rules", "Korean Travel Rules", "한국 KTX, 아시아나, 대한항공 교통 티켓 규칙")
    },
    "identity": {
        "cn": ("自提身份码与核销二维码规则库", "Pick-up Identity Rules", "包含菜鸟身份码、多多提货码、快递柜扫码核销规则")
    },
    "brands": {
        "cn": ("商超即配与餐饮品牌库", "China Retail & Food Brands", "包含美团、菜鸟、顺丰、瑞幸、蜜雪冰城等中国高频商户品牌"),
        "us": ("US Retail, Food & Express Brands", "US Retail & Express Brands", "Includes DoorDash, UberEats, FedEx, UPS, Starbucks"),
        "jp": ("コンビニ・スーパー・外食ブランド", "Japan Retail & Express Brands", "Seven-Eleven, Lawson, FamilyMart, Yamato など日本向け品牌"),
        "kr": ("한국 마트・편의점・배달 브랜드", "Korean Retail & Delivery Brands", "한국 쿠팡, 배달의민족, GS25, CU 브랜드"),
        "001": ("Global Master Brands Manifest", "Global Master Brands Manifest", "Global chain stores, express, delivery, and services registry")
    }
}

def get_country_info(country_code):
    c_code = country_code.lower()
    if c_code in COUNTRIES_MAP:
        return COUNTRIES_MAP[c_code]
    return {
        "code": c_code,
        "display_name": c_code.upper(),
        "native_lang": c_code if len(c_code) == 2 else DEFAULT_FALLBACK_LANG
    }

def generate_store_manifest():
    all_sources = []

    def register_official_file(rel_path, res_type, c_code, count=0):
        c_info = get_country_info(c_code)
        c_display = c_info.get('display_name', c_code)

        tpl = OFFICIAL_TITLE_TEMPLATES.get(res_type, {}).get(c_code)
        if tpl:
            name_native, name_en, desc = tpl
        else:
            name_native = f"{c_display} - {res_type.capitalize()} Catalog"
            name_en = f"{c_display} - {res_type.capitalize()} Catalog"
            desc = f"Official assets for {res_type} in {c_display}"

        all_sources.append({
            "id": f"official_{res_type}_{c_code}",
            "name": name_native,
            "name_en": name_en,
            "description": desc,
            "type": res_type,
            "source_type": "official",
            "country": c_code,
            "country_name": c_display,
            "rule_count": count,
            "url": f"{CDN_BASE_URL}/{rel_path.lstrip('/')}"
        })

    # 1. Rules
    for r_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'rules', '*.json')):
        fname = os.path.basename(r_file)
        rel = f"rules/{fname}"
        c_code = "001"
        if "_zh" in fname: c_code = "cn"
        elif "_en" in fname: c_code = "us"
        register_official_file(rel, "rules", c_code, count=40)

    # 2. Dictionaries
    for d_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'dictionaries', '*.json')):
        rel = f"dictionaries/{os.path.basename(d_file)}"
        fname_no_ext = os.path.splitext(os.path.basename(d_file))[0]
        c_code = "001"
        if "_zh" in fname_no_ext: c_code = "cn"
        elif "_en" in fname_no_ext: c_code = "us"
        elif "_ja" in fname_no_ext: c_code = "jp"
        elif "_ko" in fname_no_ext: c_code = "kr"
        register_official_file(rel, "dictionary", c_code, count=80)

    # 3. Travel
    for t_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'travel', '*.json')):
        fname = os.path.basename(t_file)
        if fname == 'travel_rules_manifest.json': continue
        rel = f"travel/{fname}"
        c_code = "001"
        if "_zh" in fname: c_code = "cn"
        elif "_en" in fname: c_code = "us"
        elif "_ja" in fname: c_code = "jp"
        elif "_ko" in fname: c_code = "kr"
        register_official_file(rel, "travel", c_code, count=50)

    # 4. Identity
    identity_file = os.path.join(VEHEREGO_ASSETS_DIR, 'identity', 'identity_manifest.json')
    if os.path.exists(identity_file):
        register_official_file("identity/identity_manifest.json", "identity", "cn", count=25)

    # 5. Brands Index
    for b_index in glob.glob(os.path.join(BRANDS_OUT_DIR, '*', 'index.json')):
        c_code = os.path.basename(os.path.dirname(b_index))
        rel = f"brands/{c_code}/index.json"
        register_official_file(rel, "brands", c_code, count=200)

    # 6. 合并第三方独立订阅源 (third_party_sources.json)
    third_party_items = THIRD_PARTY_CONFIG.get('third_party_sources', [])
    for tp in third_party_items:
        c_code = tp.get('country', '001')
        c_info = get_country_info(c_code)
        c_display = c_info.get('display_name', c_code)

        tp_entry = {
            "id": tp.get('id', f"tp_{c_code}"),
            "name": tp.get('name', ''),
            "name_en": tp.get('name_en', tp.get('name', '')),
            "description": tp.get('description', ''),
            "type": tp.get('type', 'rules'),
            "source_type": "third_party",
            "country": c_code,
            "country_name": c_display,
            "rule_count": tp.get('rule_count', 0),
            "url": tp.get('url', '')
        }
        all_sources.append(tp_entry)

    store_manifest_out = os.path.join(VEHEREGO_ASSETS_DIR, 'store_manifest.json')
    final_store_manifest = {
        "version": 1,
        "description": "VehereGo Certified Global Subscription Store Catalog Index",
        "updated_at": "2026-10-23T12:00:00Z",
        "cdn_base_url": CDN_BASE_URL,
        "sources": all_sources
    }

    with open(store_manifest_out, 'w', encoding='utf-8') as f:
        json.dump(final_store_manifest, f, ensure_ascii=False, indent=2)

    print(f"Store Manifest generation completed! Generated store_manifest.json with {len(all_sources)} sources.")

if __name__ == "__main__":
    generate_store_manifest()
