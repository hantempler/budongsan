from django.shortcuts import render, get_object_or_404
from django.conf import settings
from apt.models import Apt_list, Apt_purchase, Apt_jeonse, Apt_detail, Apt_ratio, Apt_jisu, Location, Apt_photo, Location
import matplotlib.pyplot as plt
from io import BytesIO
import base64
import numpy
import pandas as pd
import folium
import requests
import os
import json
import seaborn as sns
import matplotlib
from matplotlib import rc  # 여기에서 rc를 가져옵니다.
matplotlib.use('Agg')  # Non-GUI backend 설정
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json
rc('font', family='Malgun Gothic')  # 'Malgun Gothic' 폰트 사용
matplotlib.rcParams['axes.unicode_minus'] = False  # 한글 폰트 사용 시 마이너스 기호 깨짐 방지
from PIL import Image
import base64
from django.http import JsonResponse
from django.shortcuts import render, get_object_or_404
from .models import City, District, Neighborhood
from apt.models import Apt_list
from django.shortcuts import render, get_object_or_404
from .models import City, District, Neighborhood
from apt.models import Apt_list, Apt_detail

# Create your views here.

def region_info(request):
    return render(request, 'region_info.html')

def region_map(request):
    # 현재 날짜 기준으로 기본값 설정
    today = pd.to_datetime('today')
    print(today)
    selected_year = request.GET.get('year', 2024)  # 연도 기본값: 오늘의 연도
    selected_month = request.GET.get('month', 12)  # 월 기본값: 오늘의 월

    # 연도와 월을 결합하여 selected_date 생성
    selected_date = f"{selected_year}-{str(selected_month).zfill(2)}"

    # 데이터 타입 기본값 설정
    selected_data = request.GET.get('data_type', 'purchase_jisu')  # 데이터 타입 기본값: purchase_jisu


    # 데이터 타입 기본값 설정
    selected_data = request.GET.get('data_type', 'purchase_jisu')

    jisu_instance = Apt_jisu.objects.all()
    location = pd.read_csv("update_files/sigungu_code.csv")
    location.columns = ["cortarNo", "name"]
    location["cortarNo"] = location["cortarNo"].astype(str) 
    print(location)

    # 데이터 로드 및 처리
    purchase_jisu = pd.DataFrame(list(jisu_instance.values('date', 'cortarNo', 'jisu')))
    purchase_jisu["cortarNo"] = purchase_jisu["cortarNo"].map(lambda x: x[:5])
    purchase_jisu["date"] = pd.to_datetime(purchase_jisu['date']).dt.to_period("M")
    purchase_jisu = purchase_jisu.sort_values(by=["cortarNo", "date"], ascending=False)
    purchase_jisu["change"] = purchase_jisu['jisu'].pct_change(-1) * 100
    purchase_jisu = purchase_jisu[purchase_jisu["date"] == selected_date].reset_index(drop=True)
    purchase_jisu.columns = ["date", "cortarNo", "value", "change" ]
    purchase_jisu.loc[purchase_jisu["cortarNo"].isin(["5011000000", "5013000000"]), ["cortarNo"]] = "5000000000"
    print(purchase_jisu)

    jeonse_jisu = pd.DataFrame(list(jisu_instance.values('date', 'cortarNo', 'jeonse_jisu')))
    jeonse_jisu["cortarNo"] = jeonse_jisu["cortarNo"].map(lambda x: x[:5])
    jeonse_jisu["date"] = pd.to_datetime(jeonse_jisu['date']).dt.to_period("M")
    jeonse_jisu = jeonse_jisu.sort_values(by=["cortarNo", "date"], ascending=False)
    jeonse_jisu["change"] = jeonse_jisu['jeonse_jisu'].pct_change(-1) * 100
    jeonse_jisu = jeonse_jisu[jeonse_jisu["date"] == selected_date].reset_index(drop=True)
    jeonse_jisu.columns = ["date", "cortarNo", "value", "change" ]
    print(jeonse_jisu)

    purchase_py = pd.read_csv("update_files/purchase_py_cortarNo.csv")
    purchase_py = purchase_py[purchase_py["date"] == selected_date].sort_values(by="py", ascending=False).reset_index(drop=True)
    purchase_py["py"] = round(purchase_py["py"], 0)
    purchase_py["cortarNo"] = purchase_py["cortarNo"].astype(str)
    purchase_py.columns = ["date", "cortarNo", "value", "change" ]
    print(purchase_py)

    jeonse_py = pd.read_csv("update_files/jeonse_py_cortarNo.csv")
    jeonse_py = jeonse_py[jeonse_py["date"] == selected_date].sort_values(by="py", ascending=False).reset_index(drop=True)
    jeonse_py["py"] = round(jeonse_py["py"], 0)
    jeonse_py["cortarNo"] = jeonse_py["cortarNo"].astype(str)
    jeonse_py.columns = ["date", "cortarNo", "value", "change" ]
    print(jeonse_py)

    data_mapping = {
        'purchase_jisu': purchase_jisu,
        'purchase_jisu_change':purchase_jisu,
        'jeonse_jisu': jeonse_jisu,
        'jeonse_jisu_change': jeonse_jisu,
        'purchase_py': purchase_py,
        'purchase_py_change': purchase_py,
        'jeonse_py': jeonse_py,
        'jeonse_py_change': jeonse_py
    }

    selected_df = data_mapping.get(selected_data, purchase_jisu)

    selected_df = pd.merge(selected_df, location, on = "cortarNo", how = "left")
    print(selected_df)
    selected_df = selected_df.dropna()
    print(selected_df)

    # 지도 데이터 로드

    if selected_data in ["purchase_jisu", "purchase_jisu_change", "jeonse_jisu",  "jeonse_jisu_change" ]:
        with open("update_files/TL_SCCO_SIG_modified_1.json", "r", encoding="utf8") as file:
            state_geo = json.load(file)         
    else:
        with open("update_files/TL_SCCO_SIG_modified.json", "r", encoding="utf8") as file:
            state_geo = json.load(file)  


    bounds = [[33.0, 124.0], [39.0, 132.0]]
    map_center = [36.5, 127.5]
    m = folium.Map(location=map_center, zoom_start=10, tiles='cartodb positron')  # 먼저 줌 레벨을 8로 설정
    m.fit_bounds(bounds)  # fit_bounds로 지도를 범위에 맞게 조정

    # Folium 지도 초기화
    m = folium.Map(location=[36.0, 127.8424], zoom_start=7, tiles="cartodbpositron")

    # Choropleth 스타일 조정

    if selected_data in ["purchase_jisu", "jeonse_jisu", "purchase_py", "jeonse_py"]:
        columns = ['cortarNo', 'value']
    else:
        columns = ['cortarNo', 'change']


    legend_mapping = {
        'purchase_jisu': "(KB)매매지수",
        'purchase_jisu_change':"(KB)매매지수 변화율(%)",
        'jeonse_jisu': "(KB)전세지수",
        'jeonse_jisu_change': "(KB)전세지수 변화율(%)",
        'purchase_py': "매매평단가",
        'purchase_py_change': "매매평단가_증감율(%)",
        'jeonse_py': "전세평단가",
        'jeonse_py_change': "전세평단가_증감율(%)"
    }

    legend_name = legend_mapping.get(selected_data)
    title = f"{selected_date} {legend_name}"
        
    folium.Choropleth(
        geo_data=state_geo,
        name=selected_data,
        data=selected_df, 
        columns=columns,
        key_on='feature.properties.SIG_CD',
        fill_color='BuPu',  # 색상을 더 부드럽고 가독성 좋게 변경
        fill_opacity=0.7,  # 불투명도를 높여 데이터 가독성 개선
        line_opacity=0.3,  # 경계를 더 뚜렷하게 표시
        legend_name= legend_name,  # 명확한 한글 레이블
        nan_fill_color="transparent",  # 데이터가 없는 지역을 투명하게
        nan_fill_opacity=0  # 데이터 없는 지역을 완전히 투명하게
    ).add_to(m)

    # 추가 지도 컨트롤
    folium.LayerControl(position='topright').add_to(m)

    # 지도 저장 경로
    map_path = "./static/maps/apt_jisu_map.html"
    m.save(map_path)


    # 가로형 바 그래프 생성 (음수는 좌측, 양수는 우측)
    selected_df = selected_df.sort_values(by="change")  # 변화율 기준 정렬
    print(len(selected_df))

    plt.figure(figsize=(10, 30))
    colors = selected_df["change"].apply(lambda x: 'red' if x < 0 else 'blue')

    plt.barh(
        selected_df["name"], selected_df["change"], 
        color=colors, alpha=0.7
    )

    # 0 기준선 추가
    plt.axvline(0, color='black', linewidth=1.2)

    plt.xlabel('변화율 (%)', fontsize=12)
    plt.ylabel('지역 코드', fontsize=12)
    plt.title(f'{selected_data} 변화율', fontsize=14)
    plt.gca().invert_yaxis()  # 상위 지역이 위쪽에 오도록 변경
    plt.grid(axis='x', linestyle='--', alpha=0.5)
    plt.tight_layout()

    # 이미지 저장
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()
    plt.close()
    
    print(selected_data)
    selected_df = selected_df[["date", "name", "value", "change"]]
    selected_df["value"] = round(selected_df["value"], 1)
    selected_df.columns = ["기준시점", "대상지역", f'{selected_data}', "변화율(%)"]
    selected_df["변화율(%)"] = round(selected_df["변화율(%)"], 1)


    # context에 추가
    context = {
        'title' : title,
        'map_path': map_path,
        'date': selected_date,
        'data_type': selected_data,
        'selected_table' : selected_df.to_html(classes="table table-striped", index=False),
        # 'purchase_jisu': purchase_jisu.to_html(classes="table table-striped", index=False),
        # 'jeonse_jisu': jeonse_jisu.to_html(classes="table table-striped", index=False),
        # 'purchase_py': purchase_py.to_html(classes="table table-striped", index=False),
        # 'jeonse_py': jeonse_py.to_html(classes="table table-striped", index=False),
        # 'jeonse_py': jeonse_py.to_html(classes="table table-striped", index=False),
        'graph_image': img_str  # 🔹 그래프 추가
    }
    
    return render(request, 'region_map.html', context)



def location_selector(request):
    cities = City.objects.all()
    selected_city = None
    selected_district = None
    selected_neighborhood = None
    apt = None
    selected_apt = []
    districts = []
    neighborhoods = []
    apt = []
    # URL 파라미터 가져오기
    city_code = request.GET.get('city_code')
    district_code = request.GET.get('district_code')
    neighborhood_code = request.GET.get('neighborhood_code')
    apt_code = request.GET.get('apt_code')

    print("City Code:", city_code)
    print("District Code:", district_code)
    print("Neighborhood Code:", neighborhood_code)
    print("Selected Apt Code:", apt_code)


    if city_code:
        selected_city = get_object_or_404(City, city_code=city_code)
        districts = District.objects.filter(city_code=selected_city)

    if district_code:
        selected_district = get_object_or_404(District, district_code=district_code)
        neighborhoods = selected_district.neighborhoods.all()

    if neighborhood_code:
        selected_neighborhood = get_object_or_404(Neighborhood, location_code__cortarNo=neighborhood_code)
        selected_apt = Apt_list.objects.filter(cortarNo__cortarNo=neighborhood_code)

    if apt_code:
        apt = get_object_or_404(Apt_list, complexNo=apt_code)

    apt_photo = Apt_photo.objects.filter(imageKey = apt_code)
    apt_detail = Apt_detail.objects.filter(complexNo = apt_code)
    print(apt)

    return render(request, 'location_selector.html', {
        'cities': cities,
        'districts': districts,
        'neighborhoods': neighborhoods,
        'selected_city': selected_city,
        'selected_district': selected_district,
        'selected_neighborhood': selected_neighborhood,
        'selected_apt' : selected_apt,
        'apt' : apt,
        'apt_detail' : apt_detail,
        'apt_photo' : apt_photo
    })




def region_graph(request):
    cities = City.objects.all()
    selected_city = None
    selected_district = None
    districts = []

    city_code = request.GET.get('city_code')
    print(city_code)
    district_code = request.GET.get('district_code')
    print(district_code)

    if city_code:
        selected_city = get_object_or_404(City, city_code=city_code)
        districts = District.objects.filter(city_code=selected_city)

    if district_code:
        selected_district = get_object_or_404(District, district_code=district_code)

    # 한글 폰트 설정
    rc('font', family='Malgun Gothic')  # 'Malgun Gothic' 폰트 사용
    matplotlib.rcParams['axes.unicode_minus'] = False  # 한글 폰트 사용 시 마이너스 기호 깨짐 방지

    # 특정 지역에 해당하는 cortarNo로 Location 객체 가져오기
    try:
        location_0 = Location.objects.get(cortarNo=city_code)
    except Location.DoesNotExist:
        location_0 = Location.objects.get(cortarNo="90")

    # 특정 지역에 해당하는 cortarNo로 Location 객체 가져오기
    try:
        location_1 = Location.objects.get(cortarNo=district_code)
    except Location.DoesNotExist:
        location_1 = Location.objects.get(cortarNo="90")

    apt_jisu_data_0 = Apt_jisu.objects.filter(cortarNo=location_0)
    apt_jisu_data_1 = Apt_jisu.objects.filter(cortarNo=location_1)


    df_location_0 = pd.DataFrame(list(apt_jisu_data_0.values('date', 'jisu', 'jeonse_jisu')))
    df_location_0['date'] = pd.to_datetime(df_location_0['date'])
    print(f"{location_0.name}")
    print(df_location_0.head(1))



    df_location_1 = pd.DataFrame(list(apt_jisu_data_1.values('date', 'jisu', 'jeonse_jisu')))
    try:
        df_location_1['date'] = pd.to_datetime(df_location_1['date'])
    except :
        pass
    print(f"{location_1.name}")
    print(df_location_1.head(1))




    # 매매지수 그래프 생성
    plt.figure(figsize=(9, 5))
    plt.plot(
        df_location_0['date'], df_location_0['jisu'],
        marker='', linestyle='--', color='b', label=f'{location_0.name} 매매지수'
    )
    try:
        plt.plot(
            df_location_1['date'], df_location_1['jisu'],
            marker='', linestyle='-', color='r', label=f'{location_1.name} 매매지수'
        )
    except:
        pass
    plt.title(f'{location_1.name} 및 {location_0.name} 매매 지수 추이', fontsize=14)
    plt.legend()
    plt.tight_layout()

    # 매매지수 그래프 이미지 저장
    buf1 = BytesIO()
    plt.savefig(buf1, format='png')
    buf1.seek(0)
    img_str1 = base64.b64encode(buf1.getvalue()).decode('utf-8')
    buf1.close()
    plt.close()

    # 전세지수 그래프 생성
    plt.figure(figsize=(9, 5))
    plt.plot(
        df_location_0['date'], df_location_0['jeonse_jisu'],
        marker='', linestyle='--', color='g', label=f'{location_0.name} 전세지수'
    )
    try:
        plt.plot(
            df_location_1['date'], df_location_1['jeonse_jisu'],
            marker='', linestyle='-', color='orange', label=f'{location_1.name}전세지수'
        )
    except:
        pass
    plt.title(f'{location_1.name} 및 {location_0.name} 전세 지수 추이', fontsize=14)
    plt.legend()
    plt.tight_layout()

    # 전세지수 그래프 이미지 저장
    buf2 = BytesIO()
    plt.savefig(buf2, format='png')
    buf2.seek(0)
    img_str2 = base64.b64encode(buf2.getvalue()).decode('utf-8')
    buf2.close()
    plt.close()



















    return render(request, 'region_graph.html', {
        'cities': cities,
        'districts': districts,
        'selected_city': selected_city,
        'selected_district': selected_district,
        'location': location_1,
        'img_str1': img_str1,  # 매매지수 그래프
        'img_str2': img_str2,  # 전세지수 그래프
    })

