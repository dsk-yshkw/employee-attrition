import pandas as pd


class EmploymentFeatureBuilder:
    def build(self, df: pd.DataFrame) -> pd.DataFrame:
        out = pd.DataFrame(index=df.index)
        out["employment_type"] = df.get("Q17")     # 就業形態
        out["contract_type"] = df.get("Q18")       # 雇用形態（正規/非正規）
        out["industry"] = df.get("Q28")            # 業種
        out["firm_size"] = df.get("Q29")           # 従業員規模
        out["occupation"] = df.get("Q30")          # 職種
        out["has_fixed_term"] = df.get("Q31")      # 有期雇用か
        out["weekly_work_days"] = pd.to_numeric(df.get("Q34_1"), errors="coerce")
        out["weekly_work_hours"] = pd.to_numeric(df.get("Q34_2"), errors="coerce")
        out["managerial_position"] = df.get("Q35") # 役職
        out["overtime_status"] = df.get("Q36")     # 残業状況
        out["commute_time"] = df.get("Q40")        # 片道通勤時間
        return out
