/**
 * Global Multi-Region SEO Keyword Matrix & Dynamic Meta Engine
 * Regional Coverage: North America (北美大区), Europe (欧洲大区), East Asia (东亚与亚太大区), Latin America (拉美大区), Middle East & South Asia (中东与南亚大区)
 * Target Base Domain: https://choicenew.github.io/pyropub/
 */

(function (global) {
    'use strict';

    var REGIONAL_SEO_MATRIX = {
        north_america: {
            region_name: "North America (北美大区)",
            locale_codes: ["en-US", "en-CA", "fr-CA", "es-MX"],
            keywords: [
                "STIR SHAKEN caller verification Android",
                "Robocall blocker spam call filter US Canada",
                "Android Live Activity status bar capsule",
                "Dynamic Island Android free app North America",
                "Parcel tracking pickup code OCR Cainiao SF Express",
                "ArXiv IEEE Nature PubMed AI paper reader",
                "Edge AI paper summarizer PDF RAG Q&A",
                "Legado alternative free novel reader Android",
                "On-device AI neural translation raw manga"
            ]
        },
        east_asia: {
            region_name: "East Asia (东亚与亚太大区)",
            locale_codes: ["zh-CN", "zh-TW", "ja-JP", "ko-KR"],
            keywords: [
                "骚扰电话拦截", "短信拦截器", "灵动岛", "状态栏胶囊",
                "取件码自动提取", "AI论文阅读器", "Legado替代品", "本地AI翻译"
            ]
        }
    };

    if (typeof module !== 'undefined' && module.exports) {
        module.exports = REGIONAL_SEO_MATRIX;
    } else {
        global.PYRO_REGIONAL_SEO_MATRIX = REGIONAL_SEO_MATRIX;
    }
})(typeof window !== 'undefined' ? window : this);
