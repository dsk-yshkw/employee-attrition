"""Map JPSED industry codes (Q30, 67 fine categories) to the JSIC major divisions
used by the MHLW Monthly Labour Survey (16 industries in
``data/macro/japan_wage_growth_industry.csv``).

The mapping is approximate (JSIC major-division level). JPSED categories with no
5+-employee MHLW counterpart (agriculture/fishing, public service, unclassified)
map to ``None`` and fall back to the all-industry rate.
"""

# JSIC division names exactly as they appear in japan_wage_growth_industry.csv
_MIN = "鉱業，採石業等"
_CON = "建設業"
_MAN = "製造業"
_ELE = "電気・ガス業"
_INF = "情報通信業"
_TRA = "運輸業，郵便業"
_WHO = "卸売業，小売業"
_FIN = "金融業，保険業"
_REA = "不動産・物品賃貸業"
_ACA = "学術研究等"
_FOO = "飲食サービス業等"
_LIV = "生活関連サービス等"
_EDU = "教育，学習支援業"
_MED = "医療，福祉"
_CMP = "複合サービス事業"
_OTH = "その他のサービス業"

# JPSED Q30 code -> JSIC division (None = no MHLW counterpart, use all-industry).
JPSED_TO_JSIC = {
    1: None,                # 農林漁業
    2: _MIN,                # 鉱業
    3: _CON, 4: _CON, 5: _CON,                              # 建設
    **{c: _MAN for c in range(6, 26)},                      # 6-25 製造業
    26: _ELE,               # 電気・ガス・熱供給・水道
    27: _INF, 28: _INF, 29: _INF, 30: _INF, 31: _INF,       # 情報通信
    32: _TRA, 33: _TRA, 34: _TRA, 35: _TRA, 36: _TRA,       # 運輸
    37: _WHO, 38: _WHO, 39: _WHO, 40: _WHO, 41: _WHO, 42: _WHO, 43: _WHO,  # 卸小売
    44: _FIN, 45: _FIN, 46: _FIN, 47: _FIN, 48: _FIN, 49: _FIN,            # 金融保険
    50: _REA,               # 不動産
    51: _FOO, 52: _FOO,     # 飲食店 / 旅館・ホテル (宿泊)
    53: _MED, 54: _MED,     # 医療 / 社会福祉
    55: _EDU,               # 教育
    56: _CMP,               # 郵便局 -> 複合サービス
    57: _LIV, 58: _LIV, 59: _LIV,   # 理美容等 / 駐車場 / その他生活関連
    60: _OTH,               # 自動車整備 -> その他サービス
    61: _REA,               # 物品賃貸 -> 不動産・物品賃貸
    62: _ACA, 63: _ACA,     # 広告 / 専門サービス -> 学術研究等
    64: _OTH, 65: _OTH,     # 事業サービス / その他サービス
    66: None,               # 公務
    67: None,               # 他に分類されないもの
}


def to_jsic(code):
    """Return the JSIC division name for a JPSED industry code, or None."""
    try:
        return JPSED_TO_JSIC.get(int(code))
    except (TypeError, ValueError):
        return None
