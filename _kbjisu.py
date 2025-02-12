import os
import sys
import django
import pandas as pd
from pathlib import Path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_prj.settings")
django.setup()

# BASE_DIR 설정 (settings.py에서 가져오는 방식과 동일)
BASE_DIR = Path(__file__).resolve().parent.parent

# 필요한 모델 가져오기
from apt.models import Apt_purchase, Apt_jeonse, Apt_current, Apt_jisu, Location

name = ["date",
90,
11,
91,
1130500000,
1121500000,
1135000000,
1132000000,
1123000000,
1144000000,
1141000000,
1120000000,
1129000000,
1117000000,
1138000000,
1111000000,
1114000000,
1126000000,
92,
1168000000,
1174000000,
1150000000,
1162000000,
1153000000,
1154500000,
1159000000,
1165000000,
1171000000,
1147000000,
1156000000,
93,
26,
2611000000,
2614000000,
2617000000,
2620000000,
2623000000,
2626000000,
2629000000,
2632000000,
2635000000,
2638000000,
2641000000,
2647000000,
2650000000,
2653000000,
2671000000,
2644000000,
27,
2711000000,
2714000000,
2717000000,
2720000000,
2723000000,
2726000000,
2729000000,
2771000000,
28,
2811000000,
2814000000,
2817700000,
2818500000,
2820000000,
2823700000,
2824500000,
2826000000,
29,
2911000000,
2914000000,
2915500000,
2917000000,
2920000000,
30,
3011000000,
3014000000,
3017000000,
3020000000,
3023000000,
31,
3111000000,
3114000000,
3117000000,
3120000000,
3171000000,
94,
95,
36,
41,
4111000000,
4111100000,
4111300000,
4111500000,
4111700000,
4113000000,
4113100000,
4113300000,
4113500000,
4128000000,
4128100000,
4128500000,
4128700000,
4117000000,
4117100000,
4117300000,
4119000000,
4119200000,
4119400000,
4119600000,
4115000000,
4121000000,
4122000000,
4127000000,
4127300000,
4127100000,
4129000000,
4131000000,
4136000000,
4146000000,
4146100000,
4146300000,
4146500000,
4139000000,
4141000000,
4143000000,
4145000000,
4137000000,
4148000000,
4150000000,
4155000000,
4157000000,
4163000000,
4125000000,
4161000000,
4159000000,
51,
5111000000,
5115000000,
5113000000,
43,
4311000000,
4311100000,
4311200000,
4311400000,
4311300000,
4313000000,
4315000000,
44,
4413000000,
4413100000,
4413300000,
4415000000,
4420000000,
4423000000,
4425000000,
4427000000,
4421000000,
52,
5211000000,
5211100000,
5211300000,
5214000000,
5213000000,
46,
4611000000,
4615000000,
4623000000,
4613000000,
47,
4711000000,
4711100000,
4711300000,
4719000000,
4729000000,
4717000000,
4715000000,
48,
4812000000,
4812500000,
4812700000,
4812300000,
4812100000,
4812900000,
4833000000,
4831000000,
4817000000,
4825000000,
4822000000,
96,
50,
97,
]



def kb_jisu(end_date):
    # 날짜 범위 설정
    date = pd.DataFrame({"date": pd.date_range(start="2006-01-01", end=end_date, freq="ME")})

    # 엑셀 파일 경로
    excel_path = "update_files/202501_월간시계열.xlsx"

    # 데이터 읽기
    purchase = pd.read_excel(excel_path, sheet_name="2.매매APT", skiprows=244, header=None, names=name)
    purchase = purchase.iloc[:, 1:]  # 첫 번째 열 제거
    purchase_jisu = pd.concat([date, purchase], axis=1)
    purchase_jisu = purchase_jisu.melt(id_vars="date", var_name="cortarNo", value_name="jisu")

    jeonse = pd.read_excel(excel_path, sheet_name="6.전세APT", skiprows=244, header=None, names=name)
    jeonse = jeonse.iloc[:, 1:]
    jeonse_jisu = pd.concat([date, jeonse], axis=1)
    jeonse_jisu = jeonse_jisu.melt(id_vars="date", var_name="cortarNo", value_name="jeonse_jisu")

    # 데이터 병합 및 타입 변환
    jisu_data = pd.merge(purchase_jisu, jeonse_jisu, on=["date", "cortarNo"], how="left")
    jisu_data["cortarNo"] = jisu_data["cortarNo"].astype(str)
    jisu_data["cortarNo"] = jisu_data["cortarNo"].apply(lambda x : x[:5])
    jisu_data = jisu_data.dropna()
    # print(jisu_data)
    # jisu_data.to_csv("kb_jisu_data.csv", index = False)

    print(jisu_data.info())  # 데이터 타입 확인
    print(jisu_data.head())  # 데이터 샘플 확인

    # 기존 데이터 삭제
    Apt_jisu.objects.all().delete()

    apt_jisu_instances = []
    failed_instances = []
    for _, row in jisu_data.iterrows():
        try:
            location_instance = Location.objects.get(cortarNo=row["cortarNo"])  # Location 객체 찾기
            apt_jisu_instances.append(
                Apt_jisu(
                    date=row["date"],
                    jisu=row["jisu"],
                    jeonse_jisu=row["jeonse_jisu"],
                    cortarNo=location_instance  # ForeignKey에는 객체를 넣어야 함
                )
            )
        except Location.DoesNotExist:
            failed_instances.append(row["cortarNo"])
            # print(f"❌ Location with cortarNo {row['cortarNo']} does not exist. Skipping...")
    print(list(set(failed_instances)))
    # 존재하는 Location 값만 삽입
    Apt_jisu.objects.bulk_create(apt_jisu_instances, batch_size=1000)

    print(f"✅ Inserted {len(apt_jisu_instances)} records into Apt_jisu table.")


    # # 데이터 삽입
    # apt_jisu_instances = [
    #     Apt_jisu(
    #         date=row["date"],
    #         jisu=row["jisu"],
    #         jeonse_jisu=row["jeonse_jisu"],
    #         cortarNo=row["cortarNo"]
    #     )
    #     for _, row in jisu_data.iterrows()
    # ]

    # Apt_jisu.objects.bulk_create(apt_jisu_instances, batch_size=1000)

    # print(f"Inserted {len(apt_jisu_instances)} records into Apt_jisu table.")


if __name__ == "__main__":
    kb_jisu("2025-01-31")
