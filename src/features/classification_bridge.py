"""Bridge the 2023 JPSED industry/occupation reclassification back to the
2017-2022 coding, so categorical features and industry-based mappings are
consistent across all waves.

JPSED renumbered BOTH the industry (Q30: 67 -> 76/77 codes) and occupation
(Q32: 224 -> 214/215 codes) classifications starting with the 2023 wave.
The number pairs below are transcribed from the official correspondence
workbook shipped with the SSJDA distribution
(【業職種対応表】JPSED_SSJDA用.xlsx, sheets ★業種対応表 / ★職種対応表).
Split/new categories with no listed pre-2023 code were resolved to the
nearest pre-2023 code by label (industry: 33->32, 39->56, 57->55, 61->52,
70->56, 75->66, 77->67); genuinely new occupations (e.g. 208 university
faculty, 209 other teachers) map to None and become missing values.
"""

import numpy as np

# new (2023+) industry code -> old (2017-2022) code; None -> np.nan
IND_NEW_TO_OLD = {1: 1, 2: 2, 3: 3, 4: 4, 5: 5, 6: 6, 7: 7, 8: 8, 9: 9, 10: 10, 11: 11, 12: 12, 13: 13, 14: 14, 15: 15, 16: 16, 17: 17, 18: 18, 19: 19, 20: 20, 21: 21, 22: 22, 23: 23, 24: 24, 25: 25, 26: 26, 27: 27, 28: 28, 29: 29, 30: 30, 31: 31, 32: 32, 33: 32, 34: 33, 35: 36, 36: 34, 37: 35, 38: 36, 39: 56, 40: 37, 41: 38, 42: 39, 43: 40, 44: 41, 45: 42, 46: 43, 47: 44, 48: 45, 49: 46, 50: 47, 51: 48, 52: 49, 53: 50, 54: 53, 55: 54, 56: 55, 57: 55, 58: 52, 59: 51, 60: 57, 61: 52, 62: 35, 63: 58, 64: 61, 65: 59, 66: 63, 67: 62, 68: 65, 69: 56, 70: 56, 71: 60, 72: 64, 73: 65, 74: 66, 75: 66, 76: 67, 77: 67}

OCC_NEW_TO_OLD = {1: 1, 2: None, 3: None, 4: 2, 5: 3, 6: 4, 7: 5, 8: 6, 9: 7, 10: 8, 11: 9, 12: 10, 13: 11, 14: 12, 15: 13, 16: 14, 17: 15, 18: 16, 19: 17, 20: 18, 21: 19, 22: 20, 23: None, 24: 21, 25: 22, 26: 23, 27: 24, 28: 25, 29: 27, 30: None, 31: 28, 32: None, 33: 29, 34: 30, 35: 31, 36: 32, 37: 33, 38: None, 39: 34, 40: 35, 41: 36, 42: 37, 43: 38, 44: 39, 45: None, 46: None, 47: None, 48: None, 49: 40, 50: 41, 51: 42, 52: 43, 53: 44, 54: 45, 55: 46, 56: 47, 57: 48, 58: 49, 59: 50, 60: 51, 61: 52, 62: 53, 63: 54, 64: 55, 65: 56, 66: 57, 67: 58, 68: 59, 69: 60, 70: 61, 71: 62, 72: 63, 73: 64, 74: 65, 75: 66, 76: 67, 77: 68, 78: 69, 79: 70, 80: 71, 81: 72, 82: 73, 83: 74, 84: 75, 85: 76, 86: 77, 87: 78, 88: 80, 89: 82, 90: 83, 91: 97, 92: 102, 93: 84, 94: 85, 95: 86, 96: 87, 97: 88, 98: 89, 99: 90, 100: 91, 101: 92, 102: 93, 103: 94, 104: 95, 105: 96, 106: 98, 107: 99, 108: 100, 109: 101, 110: None, 111: None, 112: 105, 113: 106, 114: 107, 115: 108, 116: 110, 117: 103, 118: 104, 119: 109, 120: 111, 121: 112, 122: 113, 123: 114, 124: 115, 125: 116, 126: 143, 127: 172, 128: 109, 129: 117, 130: 120, 131: 121, 132: 122, 133: 123, 134: 124, 135: 125, 136: 126, 137: 127, 138: 128, 139: 129, 140: 130, 141: 131, 142: 137, 143: 139, 144: 140, 145: 141, 146: 142, 147: 144, 148: 148, 149: 157, 150: 145, 151: 147, 152: None, 153: 161, 154: 152, 155: 150, 156: 174, 157: 173, 158: None, 159: None, 160: 206, 161: 151, 162: 166, 163: None, 164: None, 165: 167, 166: 164, 167: 146, 168: 155, 169: 175, 170: 176, 171: 177, 172: 178, 173: 179, 174: 180, 175: 181, 176: 182, 177: 183, 178: 184, 179: 185, 180: 186, 181: 187, 182: 188, 183: 189, 184: None, 185: 190, 186: 191, 187: 192, 188: 199, 189: 200, 190: 203, 191: 204, 192: 193, 193: 212, 194: 194, 195: 195, 196: 196, 197: 197, 198: 198, 199: 218, 200: 219, 201: 211, 202: 213, 203: 214, 204: 215, 205: 216, 206: 217, 207: 220, 208: None, 209: None, 210: 221, 211: 222, 212: 223, 213: None, 214: 224, 215: 224}


def harmonize_classifications(panel, year_col="year"):
    """Recode industry/occupation of 2023+ waves to the 2017-2022 coding.

    Operates in place on a copy; returns the recoded panel. Codes that have no
    pre-2023 counterpart become NaN (handled natively by the tree models).
    """
    panel = panel.copy()
    post = panel[year_col] >= 2023
    for col, mapping in (("industry", IND_NEW_TO_OLD), ("occupation", OCC_NEW_TO_OLD)):
        if col not in panel.columns:
            continue
        vals = panel.loc[post, col].map(lambda v: mapping.get(int(v), np.nan)
                                        if v == v and v is not None else np.nan)
        panel.loc[post, col] = vals.astype(float)
    return panel
