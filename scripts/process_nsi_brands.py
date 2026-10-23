import os
import json
import re
import glob

WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NSI_REPO_PATH = os.path.join(WORKSPACE, 'nsi_repo')
VEHEREGO_ASSETS_DIR = os.path.join(WORKSPACE, 'veherego_assets')
CONFIGS_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'configs')
BRANDS_OUT_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'brands')

# 使用全球高速 jsDelivr CDN 作为默认 CDN，同时支持通过环境变量覆盖
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
CATEGORY_MAPPINGS = CATEGORIES_CONFIG.get('category_mappings', {})
CATEGORY_LABELS_I18N = CATEGORIES_CONFIG.get('category_labels_i18n', {})

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

def extract_country_codes(location_set):
    countries = set()

    def _extract(item):
        if isinstance(item, str):
            item = item.strip().lower()
            if item:
                country_code = item.split('-')[0]
                if country_code:
                    countries.add(country_code)
        elif isinstance(item, (list, tuple, set)):
            for sub_item in item:
                _extract(sub_item)

    _extract(location_set)
    return list(countries) if countries else ['001']

def generate_slug(display_name, wikidata, item_id=""):
    slug = re.sub(r'[^a-zA-Z0-9]', '', display_name.lower())
    if wikidata:
        slug += f"_{wikidata.lower()}"
    if not slug and item_id:
        slug = re.sub(r'[^a-zA-Z0-9]', '', item_id.lower())
    return slug or "unknown_brand"

def process():
    os.makedirs(BRANDS_OUT_DIR, exist_ok=True)

    logo_manifest = {}
    logo_manifest_path = os.path.join(NSI_REPO_PATH, 'localbrand', 'logo_manifest.json')
    if os.path.exists(logo_manifest_path):
        try:
            with open(logo_manifest_path, 'r', encoding='utf-8') as f:
                logo_manifest = json.load(f)
        except Exception as e:
            print(f"Failed to read logo_manifest.json: {e}")

    brand_data = {}

    json_files = glob.glob(os.path.join(NSI_REPO_PATH, 'localbrand', '**', '*.json'), recursive=True)
    if not json_files:
        json_files = glob.glob(os.path.join(NSI_REPO_PATH, 'brands', '**', '*.json'), recursive=True)

    for file_path in json_files:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Failed to read {file_path}: {e}")
            continue

        props = data.get('properties', {})
        nsi_path = props.get('path', '')
        nsi_type = nsi_path.replace('brands/', '').replace('localbrand/', '')

        mapped = None
        for key, val in CATEGORY_MAPPINGS.items():
            if nsi_type.startswith(key):
                mapped = (val.get('category', 'other'), val.get('sub_category', 'general'), val.get('default_color', '#14B8A6'))
                break

        if not mapped:
            if nsi_type.startswith('amenity/'):
                mapped = ('food', 'general', '#F97316')
            elif nsi_type.startswith('shop/'):
                mapped = ('supermarket', 'general', '#16A34A')
            elif nsi_type.startswith('office/'):
                mapped = ('express', 'general', '#3B82F6')
            else:
                mapped = ('other', 'general', '#14B8A6')

        cat, sub_cat, default_color = mapped
        items = data.get('items', [])

        for item in items:
            display_name = item.get('displayName', '')
            if not display_name:
                continue

            tags = item.get('tags', {})
            item_id = item.get('id', '')
            wikidata = tags.get('brand:wikidata') or tags.get('name:wikidata') or ''

            location_set_obj = item.get('locationSet')
            if isinstance(location_set_obj, dict):
                location_include = location_set_obj.get('include', ['001'])
            else:
                location_include = ['001']

            country_codes = extract_country_codes(location_include)
            slug = generate_slug(display_name, wikidata, item_id)

            icon_url = None
            if item_id in logo_manifest and isinstance(logo_manifest[item_id], dict):
                icon_url = logo_manifest[item_id].get('github_logo_url')

            website = tags.get('website', '')
            domain = None
            if website and isinstance(website, str):
                match = re.search(r'https?://(?:www\.)?([^/]+)', website)
                if match:
                    domain = match.group(1)

            for country in country_codes:
                c_info = get_country_info(country)
                native_lang = c_info.get('native_lang', 'en')

                local_title = (tags.get(f'name:{native_lang}') or
                               tags.get(f'brand:{native_lang}') or
                               tags.get('name') or
                               tags.get('brand') or
                               display_name)

                en_fallback = (tags.get('name:en') or
                               tags.get('brand:en') or
                               tags.get('name') or
                               tags.get('brand') or
                               display_name)

                brand_item = {
                    "slug": slug,
                    "title": local_title,
                    "title_en": en_fallback,
                    "category": cat,
                    "sub_category": sub_cat,
                    "color": default_color,
                    "icon_url": icon_url,
                    "domain": domain,
                    "custom_metadata": {
                        "nsi_id": item_id,
                        "wikidata": wikidata
                    }
                }

                if country not in brand_data:
                    brand_data[country] = {}
                if cat not in brand_data[country]:
                    brand_data[country][cat] = {}

                brand_data[country][cat][slug] = brand_item

    for country, cats in brand_data.items():
        country_dir = os.path.join(BRANDS_OUT_DIR, country)
        os.makedirs(country_dir, exist_ok=True)

        for cat, brands_dict in cats.items():
            out_file = os.path.join(country_dir, f"{cat}.json")

            out_json = {
                "type": "brand",
                "version": 6,
                "source": "nsi_auto_generated",
                "country": country,
                "category": cat,
                "total_brands": len(brands_dict),
                "brand_aliases": brands_dict
            }

            with open(out_file, 'w', encoding='utf-8') as f:
                json.dump(out_json, f, ensure_ascii=False, indent=2)

        index_file = os.path.join(country_dir, "index.json")
        c_info = get_country_info(country)
        index_data = {
            "type": "brand_index",
            "country": country,
            "country_name": c_info.get('display_name', country),
            "total_categories": len(cats),
            "manifest_files": [f"{cat}.json" for cat in cats.keys()]
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    # 自动化全量资产扫描与 Store Manifest 生成
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

    # 6. 合并第三方订阅源 (third_party_sources.json)
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

    print(f"Data processing completed! Generated {len(brand_data)} country folders & store_manifest.json with {len(all_sources)} total sources.")

if __name__ == "__main__":
    process()
