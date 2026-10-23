import os
import json
import re
import glob

WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
NSI_REPO_PATH = os.path.join(WORKSPACE, 'nsi_repo')
VEHEREGO_ASSETS_DIR = os.path.join(WORKSPACE, 'veherego_assets')
CONFIGS_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'configs')
BRANDS_OUT_DIR = os.path.join(VEHEREGO_ASSETS_DIR, 'brands')

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

DEFAULT_FALLBACK_LANG = COUNTRY_LANGS_CONFIG.get('default_fallback_lang', 'en')
COUNTRIES_MAP = COUNTRY_LANGS_CONFIG.get('countries', {})
CATEGORY_MAPPINGS = CATEGORIES_CONFIG.get('category_mappings', {})

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

def count_items_in_json(rel_path):
    """动态统计目标 JSON 文件中的真实条数 (规则数、品牌数或词典数)"""
    abs_path = os.path.join(VEHEREGO_ASSETS_DIR, rel_path)
    if not os.path.exists(abs_path):
        return 0
    try:
        with open(abs_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            if isinstance(data, dict):
                if 'brand_aliases' in data and isinstance(data['brand_aliases'], dict):
                    return len(data['brand_aliases'])
                if 'rules' in data and isinstance(data['rules'], list):
                    return len(data['rules'])
                if 'smart_rules' in data and isinstance(data['smart_rules'], list):
                    return len(data['smart_rules'])
                if 'transit_types' in data and isinstance(data['transit_types'], dict):
                    return len(data['transit_types'])
                if 'identity_rules' in data and isinstance(data['identity_rules'], list):
                    return len(data['identity_rules'])
                if 'manifest_files' in data and isinstance(data['manifest_files'], list):
                    country_dir = os.path.dirname(abs_path)
                    total_c = 0
                    for m_file in data['manifest_files']:
                        m_path = os.path.join(country_dir, m_file)
                        if os.path.exists(m_path):
                            try:
                                with open(m_path, 'r', encoding='utf-8') as mf:
                                    m_data = json.load(mf)
                                    if 'brand_aliases' in m_data and isinstance(m_data['brand_aliases'], dict):
                                        total_c += len(m_data['brand_aliases'])
                            except Exception:
                                pass
                    return total_c
            elif isinstance(data, list):
                return len(data)
    except Exception as e:
        print(f"Failed to count items in {rel_path}: {e}")
    return 0

def process_brands():
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
                "type": "brand_catalog",
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
            "type": "brand_catalog_index",
            "country": country,
            "country_name": c_info.get('display_name', country),
            "total_categories": len(cats),
            "manifest_files": [f"{cat}.json" for cat in cats.keys()]
        }

        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, ensure_ascii=False, indent=2)

    print(f"NSI Brands processing completed! Generated brand files for {len(brand_data)} countries.")

def generate_store_manifest():
    """动态编译生成 100% 自动计算真实数字的商店配置文件 store_manifest.json"""
    store_config = load_json_config('store_config.json', {})
    store_config['type'] = 'store_manifest'
    sources = store_config.get('sources', store_config.get('official_sources', []))
    store_config['sources'] = sources
    if 'official_sources' in store_config:
        del store_config['official_sources']

    for item in sources:
        rel_url = item.get('url', '')
        rel_path = ''
        if 'veherego_assets/' in rel_url:
            rel_path = rel_url.split('veherego_assets/')[1]

        if rel_path:
            real_count = count_items_in_json(rel_path)
            if real_count > 0:
                item['rule_count'] = real_count

    out_store_path = os.path.join(VEHEREGO_ASSETS_DIR, 'store_manifest.json')
    with open(out_store_path, 'w', encoding='utf-8') as f:
        json.dump(store_config, f, ensure_ascii=False, indent=2)

    print("Store manifest processing completed with 100% dynamically computed real item counts!")

if __name__ == "__main__":
    process_brands()
    generate_store_manifest()
