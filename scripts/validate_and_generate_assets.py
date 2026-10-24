import os
import json
import glob

WORKSPACE = os.environ.get('GITHUB_WORKSPACE', os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
VEHEREGO_ASSETS_DIR = os.path.join(WORKSPACE, 'veherego_assets')

def clean_and_normalize_json_file(file_path, expected_type):
    if not os.path.exists(file_path):
        return
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        if isinstance(data, dict):
            # 强制覆盖矫正为 100% 绝对纯净的标准 2-word snake_case 标头
            data['type'] = expected_type
            if 'version' not in data:
                data['version'] = 1

            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"Cleaned & normalized {os.path.relpath(file_path, VEHEREGO_ASSETS_DIR)} -> type: '{expected_type}'")
    except Exception as e:
        print(f"Error processing {file_path}: {e}")

def run_all_asset_cleaners():
    print("Starting total asset JSON header normalization...")

    # 1. App Bridge Rules (veherego_assets/rules/*.json -> type: app_rules)
    for r_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'rules', '*.json')):
        clean_and_normalize_json_file(r_file, 'app_rules')

    # 2. Smart Status Dictionaries (veherego_assets/dictionaries/*.json -> type: smart_dictionary)
    for d_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'dictionaries', '*.json')):
        clean_and_normalize_json_file(d_file, 'smart_dictionary')

    # 3. Travel Rules (veherego_assets/travel/*.json -> type: travel_rules)
    for t_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'travel', '*.json')):
        fname = os.path.basename(t_file)
        if fname == 'travel_rules_manifest.json':
            clean_and_normalize_json_file(t_file, 'travel_rules_manifest')
        else:
            clean_and_normalize_json_file(t_file, 'travel_rules')

    # 4. Identity Rules (veherego_assets/identity/*.json -> type: identity_rules)
    for i_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'identity', '*.json')):
        clean_and_normalize_json_file(i_file, 'identity_rules')

    # 5. Brands Master Manifest (veherego_assets/brands/brands_manifest.json -> type: brand_catalog)
    master_brand = os.path.join(VEHEREGO_ASSETS_DIR, 'brands', 'brands_manifest.json')
    clean_and_normalize_json_file(master_brand, 'brand_catalog')

    # 6. Brands Category JSONs (*.json -> type: brand_catalog) and Country Index JSONs (index.json -> type: brand_catalog_index)
    for b_file in glob.glob(os.path.join(VEHEREGO_ASSETS_DIR, 'brands', '**', '*.json'), recursive=True):
        fname = os.path.basename(b_file)
        if fname in ['brands_manifest.json', 'brands_manifest_template.json']:
            continue
        if fname == 'index.json':
            clean_and_normalize_json_file(b_file, 'brand_catalog_index')
        else:
            clean_and_normalize_json_file(b_file, 'brand_catalog')

    print("Total asset JSON header normalization completed successfully!")

if __name__ == "__main__":
    run_all_asset_cleaners()
