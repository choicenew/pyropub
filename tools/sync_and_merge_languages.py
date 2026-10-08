#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
多源翻译支持语言纯 Diff 差异比对、合并与治理引擎 (母语自称 Autonym 版)
1. 【母语自称 Autonym 映射】：支持将各语言全量映射为母语原生显示名 (如 "日本語", "Français", "Deutsch", "简体中文", "Azərbaycanca")。
2. 【纯集合差异比对 (Set Difference)】：比对新老数据交集、新增集 (added) 与缺失集 (removed)，计算重合相似度。
3. 【突变防劣化保护】：若新抓取数据与老版本重合率极低或遭遇空截断，保留历史版本并输出差异警报。
4. 【多路径同步写入】：自动将产物同步导出至根目录与 pyro_api_translate 资产目录。
"""
import os
import sys
import csv
import json
from collections import OrderedDict
from datetime import datetime

# 全量 ISO 代码与语言名称 -> 母语自称 (Autonym) 权威映射字典
ISO_AND_NAME_TO_AUTONYM = {
    # 特殊标识
    "auto": "Auto",
    "all": "Auto",
    "自动": "Auto",
    "自动 (Auto)": "Auto",

    # 中文系列及方言/古汉语
    "zh": "简体中文",
    "zh-cn": "简体中文",
    "zh-CN": "简体中文",
    "zh-chs": "简体中文",
    "zh-CHS": "简体中文",
    "zh-hans": "简体中文",
    "zh-Hans": "简体中文",
    "中文": "简体中文",
    "简体中文": "简体中文",

    "zh-tw": "繁體中文",
    "zh-TW": "繁體中文",
    "zh-hant": "繁體中文",
    "zh-Hant": "繁體中文",
    "中文(台湾)": "繁體中文",
    "繁体中文": "繁體中文",
    "繁體中文": "繁體中文",

    "zh-hk": "繁體中文 (香港)",
    "zh-HK": "繁體中文 (香港)",
    "中文(香港)": "繁體中文 (香港)",
    "繁体中文(香港)": "繁體中文 (香港)",

    "yue": "粵語",
    "中文(粤语)": "粵語",
    "粤语": "粵語",
    "粵語": "粵語",

    "wyw": "文言文",
    "lzh": "文言文",
    "中文(文言文)": "文言文",
    "文言文": "文言文",

    # 国内少数民族语言
    "bo": "བོད་སྐད",
    "藏语": "བོད་སྐད",
    "za": "Vahcuengh",
    "壮语": "Vahcuengh",
    "hmn": "Hmoob",
    "苗语": "Hmoob",
    "ii": "ꆈꌠꉙ",
    "彝语": "ꆈꌠꉙ",
    "mn": "Монгол",
    "蒙古语": "Монгол",
    "mn-Cyrl": "Монгол (Кирилл)",
    "蒙古语(西里尔文)": "Монгол (Кирилл)",
    "mn-Mong": "ᠮᠣᠩᠭᠣᠯ",
    "蒙古语(传统蒙古字母)": "ᠮᠣᠩᠭᠣᠯ",

    # 主要通用语言
    "en": "English",
    "eng": "English",
    "英语": "English",
    "en-us": "English (US)",
    "en-US": "English (US)",
    "英语(美国)": "English (US)",
    "en-uk": "English (UK)",
    "en-UK": "English (UK)",
    "en-gb": "English (UK)",
    "en-GB": "English (UK)",
    "英语(英国)": "English (UK)",
    "en-au": "English (Australia)",
    "en-AU": "English (Australia)",
    "英语(澳大利亚)": "English (Australia)",

    "ja": "日本語",
    "jp": "日本語",
    "jpn": "日本語",
    "日语": "日本語",

    "ko": "한국어",
    "kor": "한국어",
    "韩语": "한국어",

    "fr": "Français",
    "fra": "Français",
    "法语": "Français",
    "fr-ca": "Français (Canada)",
    "fr-CA": "Français (Canada)",
    "加拿大法语": "Français (Canada)",
    "fr-fr": "Français (France)",
    "fr-FR": "Français (France)",

    "de": "Deutsch",
    "deu": "Deutsch",
    "ger": "Deutsch",
    "德语": "Deutsch",

    "es": "Español",
    "spa": "Español",
    "西班牙语": "Español",
    "es-es": "Español (España)",
    "es-ES": "Español (España)",
    "es-mx": "Español (México)",
    "es-MX": "Español (México)",
    "西班牙语(墨西哥)": "Español (México)",
    "es-us": "Español (Estados Unidos)",
    "es-US": "Español (Estados Unidos)",
    "西班牙语(美国)": "Español (Estados Unidos)",
    "es-419": "Español (Latinoamérica)",
    "西班牙语(拉丁美洲)": "Español (Latinoamérica)",

    "ru": "Русский",
    "rus": "Русский",
    "俄语": "Русский",

    "it": "Italiano",
    "ita": "Italiano",
    "意大利语": "Italiano",

    "pt": "Português",
    "por": "Português",
    "葡萄牙语": "Português",
    "pt-br": "Português (Brasil)",
    "pt-BR": "Português (Brasil)",
    "葡萄牙语(巴西)": "Português (Brasil)",
    "pt-pt": "Português (Portugal)",
    "pt-PT": "Português (Portugal)",
    "葡萄牙语(葡萄牙)": "Português (Portugal)",

    "th": "ไทย",
    "tha": "ไทย",
    "泰语": "ไทย",

    "vi": "Tiếng Việt",
    "vie": "Tiếng Việt",
    "越南语": "Tiếng Việt",

    "id": "Bahasa Indonesia",
    "ind": "Bahasa Indonesia",
    "印尼语": "Bahasa Indonesia",
    "印度尼西亚语": "Bahasa Indonesia",

    "ar": "العربية",
    "ara": "العربية",
    "阿拉伯语": "العربية",
    "ar-ae": "العربية (الإمارات)",
    "ar-AE": "العربية (الإمارات)",
    "阿拉伯语(阿联酋)": "العربية (الإمارات)",
    "ar-eg": "العربية (مصر)",
    "ar-EG": "العربية (مصر)",
    "阿拉伯语(埃及)": "العربية (مصر)",
    "ar-sa": "العربية (السعودية)",
    "ar-SA": "العربية (السعودية)",
    "阿拉伯语(沙特阿拉伯)": "العربية (السعودية)",

    "hi": "हिन्दी",
    "hin": "हिन्दी",
    "印地语": "हिन्दी",

    "tr": "Türkçe",
    "tur": "Türkçe",
    "土耳其语": "Türkçe",

    "pl": "Polski",
    "pol": "Polski",
    "波兰语": "Polski",

    "nl": "Nederlands",
    "nld": "Nederlands",
    "荷兰语": "Nederlands",

    "sv": "Svenska",
    "swe": "Svenska",
    "瑞典语": "Svenska",

    "el": "Ελληνικά",
    "ell": "Ελληνικά",
    "希腊语": "Ελληνικά",
    "现代希腊语": "Ελληνικά",

    "he": "עברית",
    "heb": "עברית",
    "iw": "עברית",
    "希伯来语": "עברית",

    "cs": "Čeština",
    "ces": "Čeština",
    "cze": "Čeština",
    "捷克语": "Čeština",

    "da": "Dansk",
    "dan": "Dansk",
    "丹麦语": "Dansk",

    "fi": "Suomi",
    "fin": "Suomi",
    "芬兰语": "Suomi",

    "hu": "Magyar",
    "hun": "Magyar",
    "匈牙利语": "Magyar",

    "no": "Norsk",
    "nor": "Norsk",
    "nob": "Norsk",
    "nno": "Norsk",
    "挪威语": "Norsk",

    "ro": "Română",
    "ron": "Română",
    "rum": "Română",
    "罗马尼亚语": "Română",

    "sk": "Slovenčina",
    "slk": "Slovenčina",
    "slo": "Slovenčina",
    "斯洛伐克语": "Slovenčina",

    "uk": "Українська",
    "ukr": "Українська",
    "乌克兰语": "Українська",

    "bg": "Български",
    "bul": "Български",
    "保加利亚语": "Български",

    "ca": "Català",
    "cat": "Català",
    "加泰罗尼亚语": "Català",

    "hr": "Hrvatski",
    "hrv": "Hrvatski",
    "hbs": "Hrvatski",
    "克罗地亚语": "Hrvatski",

    "lt": "Lietuvių",
    "lit": "Lietuvių",
    "立陶宛语": "Lietuvių",

    "lv": "Latviešu",
    "lav": "Latviešu",
    "拉脱维亚语": "Latviešu",

    "sr": "Српски",
    "srp": "Српски",
    "塞尔维亚语": "Српски",

    "sl": "Slovenščina",
    "slv": "Slovenščina",
    "斯洛文尼亚语": "Slovenščina",

    "et": "Eesti",
    "est": "Eesti",
    "爱沙尼亚语": "Eesti",

    "fa": "فارسی",
    "fas": "فارسی",
    "per": "فارسی",
    "波斯语": "فارسی",

    "az": "Azərbaycanca",
    "aze": "Azərbaycanca",
    "阿塞拜疆语": "Azərbaycanca",

    "hy": "Հայերեն",
    "hye": "Հայերեն",
    "arm": "Հայերեն",
    "亚美尼亚语": "Հայերեն",

    "ka": "ქართული",
    "kat": "ქართული",
    "geo": "ქართული",
    "格鲁吉亚语": "ქართული",

    "kk": "Қазақ тілі",
    "kaz": "Қазақ тілі",
    "哈萨克语": "Қазақ тілі",

    "ky": "Кыргызча",
    "kir": "Кыргызча",
    "吉尔吉斯语": "Кыргызча",
    "吉尔吉斯斯坦语": "Кыргызча",

    "uz": "Oʻzbekcha",
    "uzb": "Oʻzbekcha",
    "乌兹别克语": "Oʻzbekcha",

    "ur": "اردو",
    "urd": "اردو",
    "乌尔都语": "اردو",

    "bn": "বাংলা",
    "ben": "বাংলা",
    "孟加拉语": "বাংলা",

    "ta": "தமிழ்",
    "tam": "தமிழ்",
    "泰米尔语": "தமிழ்",

    "te": "తెలుగు",
    "tel": "తెలుగు",
    "泰卢固语": "తెలుగు",

    "mr": "मराठी",
    "mar": "मराठी",
    "马拉地语": "मराठी",

    "gu": "ગુજરાતી",
    "guj": "ગુજરાતી",
    "古吉拉特语": "ગુજરાતી",

    "kn": "ಕನ್ನಡ",
    "kan": "ಕನ್ನಡ",
    "卡纳达语": "ಕನ್ನಡ",

    "ml": "മലയാളം",
    "mal": "മലയാളം",
    "马拉雅拉姆语": "മലയാളം",

    "my": "မြန်မာဘာသာ",
    "mya": "မြန်မာဘာသာ",
    "bur": "မြန်မာဘာသာ",
    "缅甸语": "မြန်မာဘာသာ",

    "km": "ភាសាខ្មែរ",
    "khm": "ភាសាខ្មែរ",
    "hkm": "ភាសាខ្មែរ",
    "高棉语": "ភាសាខ្មែរ",

    "lo": "ພາສາລາວ",
    "lao": "ພາສາລາວ",
    "老挝语": "ພາສາລາວ",

    "am": "አማርኛ",
    "amh": "አማርኛ",
    "阿姆哈拉语": "አማርኛ",

    "sw": "Kiswahili",
    "swa": "Kiswahili",
    "斯瓦希里语": "Kiswahili",

    "fil": "Filipino",
    "tl": "Filipino",
    "tgl": "Filipino",
    "菲律宾语": "Filipino",

    "ms": "Bahasa Melayu",
    "msa": "Bahasa Melayu",
    "may": "Bahasa Melayu",
    "马来语": "Bahasa Melayu",

    "af": "Afrikaans",
    "afr": "Afrikaans",
    "南非语": "Afrikaans",

    "is": "Íslenska",
    "isl": "Íslenska",
    "ice": "Íslenska",
    "冰岛语": "Íslenska",

    "ga": "Gaeilge",
    "gle": "Gaeilge",
    "爱尔兰语": "Gaeilge",

    "sq": "Shqip",
    "sqi": "Shqip",
    "alb": "Shqip",
    "阿尔巴尼亚语": "Shqip",

    "eu": "Euskara",
    "eus": "Euskara",
    "baq": "Euskara",
    "巴斯克语": "Euskara",

    "gl": "Galego",
    "glg": "Galego",
    "加利西亚语": "Galego",

    "bs": "Bosanski",
    "bos": "Bosanski",
    "波斯尼亚语": "Bosanski",

    "mk": "Македонски",
    "mkd": "Македонски",
    "mac": "Македонски",
    "马其顿语": "Македонски",

    "mt": "Malti",
    "mlt": "Malti",
    "马耳他语": "Malti",

    "cy": "Cymraeg",
    "cym": "Cymraeg",
    "wel": "Cymraeg",
    "威尔士语": "Cymraeg",

    "yi": "ייִדיש",
    "yid": "ייִדיش",
    "意第绪语": "ייִדיש",

    "yo": "Yorùbá",
    "yor": "Yorùbá",
    "约鲁巴语": "Yorùbá",

    "ig": "Ásụ̀sụ́ Ìgbò",
    "ibo": "Ásụ̀sụ́ Ìgbò",
    "伊博语": "Ásụ̀sụ́ Ìgbò",

    "ha": "Harshen Hausa",
    "hau": "Harshen Hausa",
    "豪萨语": "Harshen Hausa",

    "so": "Soomaali",
    "som": "Soomaali",
    "索马里语": "Soomaali",

    "st": "Sesotho",
    "sot": "Sesotho",
    "塞索托语": "Sesotho",

    "su": "Basa Sunda",
    "sun": "Basa Sunda",
    "巽他语": "Basa Sunda",

    "jv": "Basa Jawa",
    "jav": "Basa Jawa",
    "jw": "Basa Jawa",
    "爪哇语": "Basa Jawa",

    "ceb": "Cebuano",
    "宿务语": "Cebuano",

    "ny": "Chichewa",
    "nya": "Chichewa",
    "齐切瓦语": "Chichewa",

    "mg": "Malagasy",
    "mlg": "Malagasy",
    "马尔加什语": "Malagasy",

    "ht": "Kreyòl ayisyen",
    "hat": "Kreyòl ayisyen",
    "海地克里奥尔语": "Kreyòl ayisyen",

    "haw": "ʻŌlelo Hawaiʻi",
    "hawai": "ʻŌlelo Hawaiʻi",
    "夏威夷语": "ʻŌlelo Hawaiʻi",

    "mi": "Te Reo Māori",
    "mri": "Te Reo Māori",
    "mao": "Te Reo Māori",
    "毛利语": "Te Reo Māori",

    "sm": "Gagana Samoa",
    "smo": "Gagana Samoa",
    "萨摩亚语": "Gagana Samoa",

    "tg": "Тоҷикӣ",
    "tgk": "Тоҷикӣ",
    "塔吉克语": "Тоҷикӣ",

    "tk": "Türkmen dili",
    "tuk": "Türkmen dili",
    "土库曼语": "Türkmen dili",

    "tt": "Татарча",
    "tat": "Татарча",
    "鞑靼语": "Татарча",

    "ug": "ئۇيغۇرچە",
    "uig": "ئۇيغۇرچە",
    "维吾尔语": "ئۇيغۇرچە",

    "ps": "پښتو",
    "pus": "پښتو",
    "普什图语": "پښتو",

    "sd": "سنڌي",
    "snd": "سنڌي",
    "信德语": "سنڌي",

    "ne": "नेपाली",
    "nep": "नेपाली",
    "尼泊尔语": "नेपाली",

    "si": "සිංහල",
    "sin": "සිංහල",
    "僧伽罗语": "සිංහල",

    "pa": "ਪੰਜਾਬੀ",
    "pan": "ਪੰਜਾਬੀ",
    "旁遮普语": "ਪੰਜਾਬੀ",

    "fy": "Frysk",
    "fry": "Frysk",
    "弗里斯兰语": "Frysk",
    "西弗里斯兰语": "Frysk",

    "co": "Corsu",
    "cos": "Corsu",
    "科西嘉语": "Corsu",

    "gd": "Gàidhlig",
    "gla": "Gàidhlig",
    "苏格兰盖尔语": "Gàidhlig",

    "lb": "Lëtzebuergesch",
    "ltz": "Lëtzebuergesch",
    "卢森堡语": "Lëtzebuergesch",

    "la": "Latina",
    "lat": "Latina",
    "拉丁语": "Latina",

    "eo": "Esperanto",
    "epo": "Esperanto",
    "世界语": "Esperanto",

    "ku": "Kurdî",
    "kur": "Kurdî",
    "库尔德语": "Kurdî",

    "ckb": "کوردی",
    "库尔德语(中)": "کوردی",
    "库尔德语(索拉尼)": "کوردی",

    "ti": "ትግርኛ",
    "tir": "ትግርኛ",
    "提格利尼亚语": "ትግርኛ",

    "ay": "Aymar aru",
    "aym": "Aymar aru",
    "艾马拉语": "Aymar aru",

    "qu": "Runa Simi",
    "que": "Runa Simi",
    "克丘亚语": "Runa Simi",

    "sn": "chiShona",
    "sna": "chiShona",
    "肖纳语": "chiShona",

    "zu": "isiZulu",
    "zul": "isiZulu",
    "祖鲁语": "isiZulu",
}

def try_import_translators():
    try:
        import translators as ts
        return ts
    except ImportError:
        root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        local_ts = os.path.join(root_dir, "translators")
        if os.path.exists(local_ts):
            sys.path.insert(0, local_ts)
            try:
                import translators as ts
                return ts
            except Exception:
                pass
        try:
            import subprocess
            print("正在安装 UlionTse/translators 依赖...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "translators"], timeout=60)
            import translators as ts
            return ts
        except Exception as e:
            print(f"提示: 未能在线加载 translators ({e})，将使用历史归档源与 CSV 进行比对合并。")
            return None

def compute_diff(old_list, new_list):
    """计算纯集合差异指标"""
    old_set = set(old_list)
    new_set = set(new_list)
    
    intersection = old_set & new_set
    added = new_set - old_set
    removed = old_set - new_set
    
    similarity = (len(intersection) / len(old_set) * 100.0) if len(old_set) > 0 else (100.0 if len(new_set) > 0 else 0.0)
    
    return {
        "old_count": len(old_set),
        "new_count": len(new_set),
        "common_count": len(intersection),
        "added": sorted(list(added)),
        "removed": sorted(list(removed)),
        "similarity": round(similarity, 1)
    }

def resolve_autonym(key_or_code):
    """根据键名或 ISO 代码解析出标准母语自称 (Autonym)"""
    if not key_or_code:
        return key_or_code
    s = str(key_or_code).strip()
    if s in ISO_AND_NAME_TO_AUTONYM:
        return ISO_AND_NAME_TO_AUTONYM[s]
    lower_s = s.lower()
    if lower_s in ISO_AND_NAME_TO_AUTONYM:
        return ISO_AND_NAME_TO_AUTONYM[lower_s]
    return s

def main():
    root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    csv_file = os.path.join(root_dir, "supported_language_map.csv")
    raw_sources_dir = os.path.join(root_dir, "raw_sources")
    os.makedirs(raw_sources_dir, exist_ok=True)
    
    value_order = []
    value_map = {}
    code_to_value = {}

    # 初始化内置的权威 Autonym 代码表
    for code_or_name, autonym in ISO_AND_NAME_TO_AUTONYM.items():
        code_to_value[code_or_name.lower()] = autonym
        code_to_value[code_or_name] = autonym
    
    diff_report_entries = []

    # 1. 载入本地 CSV 基础底座（使用 utf-8-sig 兼容 BOM 标头）
    if os.path.exists(csv_file):
        print(f"📖 [Step 1] 载入本地 CSV 基准映射: {csv_file}")
        with open(csv_file, mode="r", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            for row in reader:
                raw_val = row.get("Value", "").strip()
                if not raw_val:
                    continue

                # 统一转换为母语自称 (Autonym)
                autonym = resolve_autonym(raw_val)

                if autonym not in value_map:
                    value_map[autonym] = {"Value": autonym}
                    value_order.append(autonym)

                for provider, code in row.items():
                    clean_provider = provider.strip() if provider else ""
                    clean_code = code.strip() if code else ""
                    if clean_provider and clean_provider != "Value" and clean_code:
                        value_map[autonym][clean_provider] = clean_code
                        code_to_value[clean_code.lower()] = autonym
                        code_to_value[clean_code] = autonym
        print(f"✓ CSV 载入完成，基准映射归并为 {len(value_map)} 种母语条目。")

    # 2. 动态抓取 + 纯 Difference 差异比对分析
    ts = try_import_translators()
    if ts is not None:
        pool = getattr(ts, "translators_pool", [])
        print(f"🌐 [Step 2] 动态抓取与 Difference 差异分析 ({len(pool)} 个服务商)...")
        
        for provider in pool:
            provider_file = os.path.join(raw_sources_dir, f"{provider}.json")
            
            old_list = []
            if os.path.exists(provider_file):
                try:
                    with open(provider_file, "r", encoding="utf-8") as f:
                        old_list = json.load(f)
                except Exception:
                    old_list = []

            try:
                lang_dict = ts.get_languages(translator=provider)
                fetched_list = []
                if isinstance(lang_dict, dict):
                    fetched_list = [str(k).strip() for k in lang_dict.keys() if str(k).strip()]
                elif isinstance(lang_dict, (list, tuple, set)):
                    fetched_list = [str(k).strip() for k in lang_dict if str(k).strip()]

                diff = compute_diff(old_list, fetched_list)

                # 判定决策：
                if diff["new_count"] == 0 and diff["old_count"] > 0:
                    status = "🛡️ 抓取为空(保留历史)"
                    final_list = old_list
                elif diff["old_count"] > 10 and diff["similarity"] < 40.0:
                    status = f"⚠️ 差异突变(相似度 {diff['similarity']}% < 40%，触发保护)"
                    final_list = old_list
                else:
                    if diff["added"] and diff["removed"]:
                        status = f"🔄 版本变更 (+{len(diff['added'])}, -{len(diff['removed'])})"
                    elif diff["added"]:
                        status = f"✨ 新增扩展 (+{len(diff['added'])})"
                    elif diff["removed"]:
                        status = f"✂️ 上游精简 (-{len(diff['removed'])})"
                    else:
                        status = "✓ 完全一致 (100% 重合)"
                    final_list = fetched_list

                    if final_list:
                        with open(provider_file, "w", encoding="utf-8") as f:
                            json.dump(sorted(list(set(final_list))), f, ensure_ascii=False, indent=2)

                diff["status"] = status
                diff["provider"] = provider
                diff_report_entries.append(diff)
                print(f"  [{provider}] {status} | 老版本: {diff['old_count']}, 新版本: {diff['new_count']}, 重合率: {diff['similarity']}%")
            except Exception as e:
                diff = compute_diff(old_list, [])
                diff["status"] = f"✕ 抓取异常 ({e})"
                diff["provider"] = provider
                diff_report_entries.append(diff)
                print(f"  [{provider}] 抓取异常，沿用历史数据: {e}")

    # 3. 汇总合并 raw_sources/ 目录下的所有文件
    print(f"🔄 [Step 3] 汇总合并所有 Provider 数据...")
    for file_name in os.listdir(raw_sources_dir):
        if file_name.endswith(".json"):
            provider = file_name[:-5]
            file_path = os.path.join(raw_sources_dir, file_name)
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    codes = json.load(f)
                for lang_code in codes:
                    code_str = str(lang_code).strip()
                    if not code_str:
                        continue

                    # 优先获取对应的母语自称 (Autonym)
                    autonym = code_to_value.get(code_str.lower(), code_to_value.get(code_str, resolve_autonym(code_str)))

                    if autonym not in value_map:
                        value_map[autonym] = {"Value": autonym}
                        value_order.append(autonym)
                    value_map[autonym][provider] = code_str
            except Exception as e:
                print(f"  读取持久化缓存 {file_name} 警告: {e}")

    # 4. 生成标准 JSON 文件并导出至多个路径
    print(f"💾 [Step 4] 导出标准 supported_languages.json...")
    def sort_key(val_name):
        if val_name in value_order:
            return (0, value_order.index(val_name))
        return (1, val_name)

    output_list = []
    for val_name in sorted(value_map.keys(), key=sort_key):
        item = value_map[val_name]
        ordered_item = OrderedDict()
        ordered_item["Value"] = item["Value"]
        for k in sorted(item.keys()):
            if k != "Value":
                ordered_item[k] = item[k]
        output_list.append(ordered_item)

    # 写入根目录 target
    root_json = os.path.join(root_dir, "supported_languages.json")
    with open(root_json, "w", encoding="utf-8") as f:
        json.dump(output_list, f, ensure_ascii=False, indent=4)
    print(f"✓ 产物已生成 (根目录): {root_json} (语言总数: {len(output_list)})")

    # 自动同步写入 pyro_api_translate 包资源路径（如果目录存在）
    target_paths = [
        os.path.join(root_dir, "packages", "pyro_api_translate", "assets", "supported_languages.json"),
        os.path.join(root_dir, "packages", "core", "pyro_api_translate", "assets", "supported_languages.json"),
        os.path.abspath(os.path.join(root_dir, "..", "wallpaper", "packages", "core", "pyro_api_translate", "assets", "supported_languages.json")),
    ]

    for pkg_json_path in target_paths:
        pkg_dir = os.path.dirname(pkg_json_path)
        if os.path.exists(pkg_dir):
            try:
                with open(pkg_json_path, "w", encoding="utf-8") as f:
                    json.dump(output_list, f, ensure_ascii=False, indent=4)
                print(f"✓ 产物已同步写入: {pkg_json_path}")
            except Exception as e:
                print(f"  警告: 无法同步写入 {pkg_json_path}: {e}")

    # 5. 生成专业 Markdown Difference 详细对比报告并存入 raw_sources 文件夹
    report_content = []
    report_content.append("# 🌐 多源翻译语言 Difference 差异比对报告 (Autonym 母语版)\n")
    report_content.append(f"- **比对时间**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`")
    report_content.append(f"- **合并总语言条目**: `{len(output_list)}` 种\n")
    report_content.append("### 各翻译源 Difference 明细表\n")
    report_content.append("| 服务商 (Provider) | 上周数 | 本周数 | 重合交集 | 相似度 | 状态判定 | 新增代码 (Diff Added) | 移除/废弃代码 (Diff Removed) |")
    report_content.append("| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |")
    for d in sorted(diff_report_entries, key=lambda x: x["provider"]):
        added_preview = ", ".join([f"`+{c}`" for c in d["added"][:6]]) if d["added"] else "-"
        if len(d["added"]) > 6:
            added_preview += f" 等 {len(d['added'])} 个"
        removed_preview = ", ".join([f"`-{c}`" for c in d["removed"][:6]]) if d["removed"] else "-"
        if len(d["removed"]) > 6:
            removed_preview += f" 等 {len(d['removed'])} 个"
        report_content.append(f"| `{d['provider']}` | {d['old_count']} | {d['new_count']} | {d['common_count']} | `{d['similarity']}%` | {d['status']} | {added_preview} | {removed_preview} |")
    
    full_report_text = "\n".join(report_content) + "\n"

    report_file = os.path.join(raw_sources_dir, "sync_diff_report.md")
    readme_file = os.path.join(raw_sources_dir, "README.md")
    
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(full_report_text)
    with open(readme_file, "w", encoding="utf-8") as f:
        f.write(full_report_text)
    
    print(f"📋 Difference 差异分析报告已同步写入: {report_file} 和 {readme_file}")

if __name__ == "__main__":
    main()
