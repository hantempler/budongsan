import os
import sys
import django
import pandas as pd

# 프로젝트 루트를 sys.path에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Django 설정 파일 지정
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_prj.settings")

# Django 초기화
django.setup()

# 필요한 모델 가져오기
from apt.models import Apt_purchase, Apt_jeonse, Apt_list, Apt_detail

def create_mean_price():
    # Apt_list와 Apt_detail 데이터를 불러옴

    apt_list = Apt_list.objects.values("complexNo", "cortarNo", "roadAddressPrefix")
    apt_detail = Apt_detail.objects.values('complexNo', 'complexno_py', 'supplyAreaDouble')

    # pandas DataFrame으로 변환
    apt_list_df = pd.DataFrame(apt_list)
    apt_detail_df = pd.DataFrame(apt_detail)

    # apt_list와 apt_detail을 complexNo를 기준으로 병합
    selected = pd.merge(apt_detail_df, apt_list_df, on="complexNo", how='inner')

    # 필요한 컬럼 선택
    selected_1 = selected[["cortarNo", "complexno_py", "supplyAreaDouble", "roadAddressPrefix"]]

    # Apt_purchase 데이터 가져오기
    apt_purchase = Apt_purchase.objects.values('date', 'price', 'complexno_py')
    apt_jeonse = Apt_jeonse.objects.values('date', 'price', 'complexno_py')

    apt_purchase_df = pd.DataFrame(apt_purchase)
    apt_purchase_df["date"] = pd.to_datetime(apt_purchase_df["date"]).dt.to_period("M").astype(str)

    apt_jeonse_df = pd.DataFrame(apt_jeonse)
    apt_jeonse_df["date"] = pd.to_datetime(apt_jeonse_df["date"]).dt.to_period("M").astype(str)

    # apt_purchase와 selected_1을 complexno_py 기준으로 병합
    purchase_py = pd.merge(apt_purchase_df, selected_1, on="complexno_py", how="inner")
    jeonse_py = pd.merge(apt_jeonse_df, selected_1, on="complexno_py", how="inner")
    print(purchase_py.info())

    # py 계산 (가격 / 공급면적 * 3.3)
    purchase_py["py"] = round((purchase_py["price"].apply(float) / purchase_py["supplyAreaDouble"].apply(float)) * 3.3, 0)
    jeonse_py["py"] = round((jeonse_py["price"].apply(float) / jeonse_py["supplyAreaDouble"].apply(float)) * 3.3, 0)

    # 거래일을 월별로 변환
    purchase_py["date"] = pd.to_datetime(purchase_py["date"]).dt.to_period("M").astype(str)
    jeonse_py["date"] = pd.to_datetime(jeonse_py["date"]).dt.to_period("M").astype(str)

    # 월별 평균 가격 계산
    purchase_py = purchase_py.groupby(["date", "cortarNo", "roadAddressPrefix"])["py"].mean().reset_index()
    jeonse_py = jeonse_py.groupby(["date", "cortarNo", "roadAddressPrefix"])["py"].mean().reset_index()

    # cortarNo 값이 5자리로 수정
    purchase_py["cortarNo"] = purchase_py["cortarNo"].astype(str).apply(lambda x: x[:5])
    jeonse_py["cortarNo"] = jeonse_py["cortarNo"].astype(str).apply(lambda x: x[:5])
    print(purchase_py.info())
    print(jeonse_py.info())


    # cortarNo 값에 일치하는 위경도값 배치
    Lat_Lon = pd.read_csv("update_files/Lat_Lon.csv")
    Lat_Lon["cortarNo"] = Lat_Lon["cortarNo"].astype(str) 
    print(Lat_Lon.info())
    Lat_Lon = Lat_Lon[["cortarNo", "gu_Lat", "gu_Lon"]]
    purchase_py = pd.merge(purchase_py, Lat_Lon, on = "cortarNo", how = "left" )
    jeonse_py = pd.merge(jeonse_py, Lat_Lon, on = "cortarNo", how = "left" )

    # 결과 출력
    purchase_py.to_csv("update_files/purchase_py.csv", index=False)
    jeonse_py.to_csv("update_files/jeonse_py.csv", index=False)

    purchase_py_cortarNo = purchase_py.groupby(["date", "cortarNo"])["py"].mean().reset_index()
    purchase_py_cortarNo = purchase_py_cortarNo.sort_values(by = ["cortarNo", "date"], ascending = False)
    purchase_py_cortarNo["change"] = purchase_py_cortarNo['py'].pct_change(-1) * 100

    jeonse_py_cortarNo = jeonse_py.groupby(["date", "cortarNo"])["py"].mean().reset_index()
    jeonse_py_cortarNo = jeonse_py_cortarNo.sort_values(by = ["cortarNo", "date"], ascending = False)
    jeonse_py_cortarNo["change"] = jeonse_py_cortarNo['py'].pct_change(-1) * 100

    purchase_py_cortarNo.to_csv("update_files/purchase_py_cortarNo.csv", index=False)
    jeonse_py_cortarNo.to_csv("update_files/jeonse_py_cortarNo.csv", index=False)

if __name__ == "__main__":
    create_mean_price()
