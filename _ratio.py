import os
import sys
import django
import pandas as pd

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django 설정 파일 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_prj.settings")  # "_prj"를 프로젝트 이름으로 대체하세요.

# Django 초기화
django.setup()

# 필요한 모델 가져오기
from apt.models import Apt_purchase, Apt_jeonse, Apt_current, Apt_ratio


def create_ratio():
    try:
        # DB에서 데이터 가져오기
        p = Apt_purchase.objects.values("complexno_py", "price", "complexNo", "date")
        j = Apt_jeonse.objects.values("complexno_py", "price", "complexNo", "date")
        c = Apt_current.objects.values("complexno_py", "price", "jeonse", "complexNo", "date")
        p = pd.DataFrame(p)
        j = pd.DataFrame(j)
        c = pd.DataFrame(c)

        idx_max_price = p.groupby(["complexno_py"])["price"].idxmax()
        price_result = p.loc[idx_max_price, ["complexNo", "complexno_py", "price"]].reset_index(drop = True)
        price_result = price_result.rename(columns={'price': 'max_price'})
        
        # idx_max_date = p.groupby(["complexno_py"])["date"].idxmax()
        # price_date = p.loc[idx_max_date, ["complexNo", "complexno_py", "price"]].reset_index(drop = True)
        price_date = c.rename(columns={'price': 'current_price',
                                       "jeonse" : 'current_jeonse'})
        
        print(price_date)

        # idx_max_jeonse = j.groupby(["complexno_py"])["date"].idxmax()
        # jeonse_result = j.loc[idx_max_jeonse, ["complexNo", "complexno_py", "price"]].reset_index(drop = True)
        # jeonse_result = jeonse_result.rename(columns={'price': 'current_jeonse'})

        merged_df = pd.merge(price_date, price_result, on=['complexNo', 'complexno_py'], how='left')
        print(merged_df)
        merged_df["by_max"] = round(merged_df["current_price"] / merged_df["max_price"], 2)
        print(merged_df)
        merged_df["by_jeonse"] = round(merged_df["current_jeonse"] / merged_df["current_price"], 2)
        print(merged_df)
        merged_df = merged_df.dropna().reset_index(drop=True)
        print(merged_df)
        # merged_df = merged_df.reset_index(drop=True)
        merged_df.to_csv("ratio.csv", index = False)

        Apt_ratio.objects.all().delete()

        # 데이터 삽입
        apt_ratio_instances = [
            Apt_ratio(
                complexNo_id=row["complexNo"],
                complexno_py_id=row["complexno_py"],
                max_price=row["max_price"],
                current_price=row["current_price"],
                current_jeonse=row["current_jeonse"],
                by_max=row["by_max"],
                by_jeonse=row["by_jeonse"]
            )
            for _, row in merged_df.iterrows()
        ]
        
        Apt_ratio.objects.bulk_create(apt_ratio_instances)

        print(f"Inserted {len(apt_ratio_instances)} records into Apt_ratio table.")
        print(merged_df.head())
        print(len(merged_df))

        
    except Exception as e:
        print("Error occurred:", e)


if __name__ == "__main__":
    create_ratio()

