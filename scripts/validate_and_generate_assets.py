import os
import json
import glob

WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VEHEREGO_ASSETS_DIR = os.path.join(WORKSPACE, 'veherego_assets')

# 权威目录到强类型 2-word snake_case 标头 1:1 映射字典 (零 if/else 丑陋条件分支)
DIRECTORY_TYPE_MAP = {
    'rules': 'app_rules',
    'dictionaries': 'smart_dictionary',
    'travel': 'travel_rules',
    'identity': 'identity_rules',
}

def clean_file_header(file_path, expected_type):
    """强制覆写为 100% 统一规范的标准 2-word snake_case 标头"""
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            data['type'] = expected_type
            if 'version' not in data:
                data['version'] = 1

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"[OK] Normalized: {os.path.relpath(file_path, VEHEREGO_ASSETS_DIR)} -> type: '{expected_type}'")
    except Exception as e:
        print(f"[Error] Failed to normalize {file_path}: {e}")

def run_all_asset_cleaners():
    print("Starting total asset JSON header normalization (Dict Map Driven)...")

    # 1. 基础领域目录驱动清洗 (rules, dictionaries, travel, identity)
    for dir_name, target_type in DIRECTORY_TYPE_MAP.items():
        dir_path = os.path.join(VEHEREGO_ASSETS_DIR, dir_name)
        for json_file in glob.glob(os.path.join(dir_path, '*.json')):
            clean_file_header(json_file, target_type)

    # 2. 品牌领域文件清洗
    brands_dir = os.path.join(VEHEREGO_ASSETS_DIR, 'brands')

    # 2.1 品牌主清单
    clean_file_header(os.path.join(brands_dir, 'brands_manifest.json'), 'brand_catalog')

    # 2.2 国家品牌包与国家品牌索引包
    for index_file in glob.glob(os.path.join(brands_dir, '*', 'index.json')):
        clean_file_header(index_file, 'brand_catalog_index')

    for cat_file in glob.glob(os.path.join(brands_dir, '*', '*.json')):
        if not cat_file.endswith('index.json'):
            clean_file_header(cat_file, 'brand_catalog')

    print("Total asset JSON header normalization completed cleanly!")

if __name__ == "__main__":
    run_all_asset_cleaners()
