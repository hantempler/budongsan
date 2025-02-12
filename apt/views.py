from django.shortcuts import render, get_object_or_404
from django.conf import settings
from apt.models import Apt_list, Apt_purchase, Apt_jeonse, Apt_detail, Apt_ratio, Apt_jisu, Location, Apt_photo
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
from datetime import datetime
import json
rc('font', family='Malgun Gothic')  # 'Malgun Gothic' 폰트 사용
matplotlib.rcParams['axes.unicode_minus'] = False  # 한글 폰트 사용 시 마이너스 기호 깨짐 방지
from PIL import Image
import base64
from django.http import JsonResponse

# Create your views here.
def index(request):
    return render(request, "index.html")

def apt_list(request):
    # 필터링을 위한 쿼리 파라미터 가져오기
    search_prefix = request.GET.get('roadAddressPrefix', '')
    search_address = request.GET.get('roadAddress', '')
    search_name = request.GET.get('complexName', '')
    max_price_percentage = request.GET.get('max_price_percentage', None)
    jeonse_price_percentage = request.GET.get('jeonse_price_percentage', None)
    total_household = request.GET.get('totalHouseholdCount', None)
    exclusive_area = request.GET.get('exclusiveArea', None)
    useApproveYmd = request.GET.get('useApproveYmd', None)

    # 검색 조건이 하나라도 입력된 경우에만 데이터를 조회
    has_search_conditions = (
        search_prefix or search_address or search_name or max_price_percentage or jeonse_price_percentage or exclusive_area or useApproveYmd
    )

    apt_data = []
    if has_search_conditions:
        # 기본 필터링
        apt_list = Apt_list.objects.all()

        if search_prefix:
            apt_list = apt_list.filter(roadAddressPrefix__icontains=search_prefix)
        if search_address:
            apt_list = apt_list.filter(roadAddress__icontains=search_address)
        if search_name:
            apt_list = apt_list.filter(complexName__icontains=search_name)
        if total_household:
            try:
                total_household = int(total_household)  # 정수로 변환
                apt_list = apt_list.filter(totalHouseholdCount__gte=total_household) # 입력한 세대수보다 큰 세대수를 포함한 아파트만 검색
            except ValueError:
                pass  # 숫자로 변환할 수 없는 경우 필터링 제외
        if exclusive_area:
            try:
                exclusive_area = float(exclusive_area)  # 실수로 처리, 전용면적 이상을 필터링
                apt_list = apt_list.filter(
                    apt_detail__exclusiveArea__gte=exclusive_area  # 전용면적이 입력한 값 이상인 아파트 필터링
                )
            except (ValueError, TypeError):
                pass  # 전용면적이 숫자로 변환될 수 없을 경우 필터링 제외
        if useApproveYmd: # 준공일자
            try:
                useApproveYmd = int(useApproveYmd)  # 정수로 변환
                apt_list = apt_list.filter(useApproveYmd__gte=useApproveYmd) # 준공일자가 입력한 값 이상인 아파트 필터링

            except ValueError:
                pass  # 숫자로 변환할 수 없는 경우 필터링 제외
       
        # 매매가, 전세가, 최고가 정보 추가 및 필터링
        for apt in apt_list:
            details = []

            # Apt_detail 객체를 통해 각 아파트 단지의 세부 사항을 가져옵니다.
            apt_details = Apt_detail.objects.filter(complexNo=apt)
            for detail in apt_details:
                # Apt_ratio에서 관련 데이터 가져오기
                latest_ratio = Apt_ratio.objects.filter(complexNo=apt, complexno_py=detail).first()
                if not latest_ratio:
                    continue  # 데이터가 없으면 건너뜀

                # 최근 거래일 조회
                recent_purchase = Apt_purchase.objects.filter(complexNo=apt, complexno_py=detail).order_by('-date').first()

                # 최고가와 전세가 비율 필터링
                try:
                    if max_price_percentage:  # max_price_percentage가 값이 있을 경우
                        try:
                            max_price_threshold = float(max_price_percentage)  # 실수로 처리, 소수점도 고려
                            if latest_ratio.by_max is None or latest_ratio.by_max * 100 >= max_price_threshold:
                                continue  # 조건에 맞지 않으면 제외
                        except (ValueError, TypeError):
                            continue  # max_price_percentage가 숫자로 변환될 수 없을 경우 제외

                    if jeonse_price_percentage:  # jeonse_price_percentage가 값이 있을 경우
                        try:
                            jeonse_price_threshold = int(jeonse_price_percentage)  # 정수로 처리
                            if latest_ratio.by_jeonse is None or latest_ratio.by_jeonse * 100 < jeonse_price_threshold:
                                continue  # 조건에 맞지 않으면 제외
                        except (ValueError, TypeError):
                            continue  # jeonse_price_percentage가 숫자로 변환될 수 없을 경우 제외
    
                except ValueError:
                    continue  # 잘못된 값이 입력되었을 경우 제외

                # 매매가, 전세가, 최고가 정보 저장
                purchase_price = latest_ratio.current_price / 10000 if latest_ratio.current_price else None
                jeonse_price = latest_ratio.current_jeonse / 10000 if latest_ratio.current_jeonse else None
                max_price = latest_ratio.max_price / 10000 if latest_ratio.max_price else None

                # 최근 거래일을 추가
                recent_purchase_date = recent_purchase.date if recent_purchase else None

                details.append({
                    'detail': detail,
                    'latest_purchase_price': purchase_price,
                    'latest_jeonse_price': jeonse_price,
                    'max_price': max_price,
                    'purchase_to_max_ratio': latest_ratio.by_max * 100 if latest_ratio.by_max else None,
                    'jeonse_to_purchase_ratio': latest_ratio.by_jeonse * 100 if latest_ratio.by_jeonse else None,
                    'recent_purchase_date': recent_purchase_date,  # 최근 거래일 추가
                })

            if details:  # 세부 정보가 있는 경우만 추가
                apt_data.append({
                    'apt': apt,
                    'details': details,
                })

    # 컨텍스트에 데이터 전달
    context = {
        'apt_data': apt_data,
        'search_prefix': search_prefix,
        'search_address': search_address,
        'search_name': search_name,
        'max_price_percentage': max_price_percentage,
        'jeonse_price_percentage': jeonse_price_percentage,
        'exclusive_area': exclusive_area,  # 전용면적 입력 값 전달
        'no_results': not apt_data and has_search_conditions,  # 검색 조건이 있지만 결과가 없는 경우
    }

    return render(request, 'apt_list.html', context)


def apt_info(request, complexNo) :
    apt_photo = Apt_photo.objects.filter(imageKey = complexNo)
    apt_list= Apt_list.objects.get(complexNo = complexNo)

    context ={
        'apt_photo' : apt_photo,
        'apt_list' : apt_list,
        'latitude': apt_list.latitude,
        'longitude': apt_list.longitude,
    }
    return render(request, 'apt_info.html', context)

def apt_detail(request, complexno_py):
    # 데이터 가져오기
    apt_detail_instance = Apt_detail.objects.get(complexno_py=complexno_py)
    apt_list_instance = apt_detail_instance.complexNo

    details = Apt_detail.objects.filter(complexno_py=complexno_py)
    purchases = Apt_purchase.objects.filter(complexno_py=complexno_py)
    jeonses = Apt_jeonse.objects.filter(complexno_py=complexno_py)

    # pandas DataFrame으로 변환
    df = pd.DataFrame(list(purchases.values('date', 'price')))
    df_1 = pd.DataFrame(list(jeonses.values('date', 'price')))
    print(df_1)

    # date 컬럼을 날짜 형식으로 변환
    df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d')
    df_1['date'] = pd.to_datetime(df_1['date'], format='%Y-%m-%d')
    print(df)
    print(df_1)

    # 연도-월로 그룹화하여 평균 가격 계산
    df['year_month'] = df['date'].dt.to_period('M')
    df_1['year_month'] = df_1['date'].dt.to_period('M')

    purchase_avg = df.groupby('year_month')['price'].mean().reset_index(name='purchase_price')
    jeonse_avg = df_1.groupby('year_month')['price'].mean().reset_index(name='jeonse_price')
    purchase_cnt = df.groupby('year_month')['price'].count().reset_index(name='purchase_cnt')
    jeonse_cnt = df_1.groupby('year_month')['price'].count().reset_index(name='jeonse_cnt')

    # 데이터 병합
    price_data = pd.merge(purchase_avg, jeonse_avg, on='year_month', how='outer')
    price_data = pd.merge(price_data, purchase_cnt, on='year_month', how='outer')
    price_data = pd.merge(price_data, jeonse_cnt, on='year_month', how='outer')
    price_data = price_data.sort_values(by="year_month", ascending=False)



    # NaN 값 처리
    price_data['purchase_price'] = price_data['purchase_price'].fillna(method='bfill')
    price_data['jeonse_price'] = price_data['jeonse_price'].fillna(method='bfill')


    # 상승률 계산 (전월대비)
    price_data['purchase_rate'] = price_data['purchase_price'].pct_change(periods=-1) * 100  # 매매가 상승률
    price_data['jeonse_rate'] = price_data['jeonse_price'].pct_change(periods=-1) * 100  # 전세가 상승률


    price_data['purchase_rate'] = price_data['purchase_rate'].fillna(0).round(1)
    price_data['jeonse_rate'] = price_data['jeonse_rate'].fillna(0).round(1)

    # 데이터 형식 변환
    price_data["purchase_price"] = price_data["purchase_price"].apply(lambda x: "-" if pd.isna(x) else round(x / 10000, 1))
    price_data["purchase_cnt"] = price_data["purchase_cnt"].apply(lambda x: "-" if pd.isna(x) else round(x, 1))
    price_data["jeonse_price"] = price_data["jeonse_price"].apply(lambda x: "-" if pd.isna(x) else round(x / 10000, 1))
    price_data["jeonse_cnt"] = price_data["jeonse_cnt"].apply(lambda x: "-" if pd.isna(x) else round(x, 1))
    price_data["purchase_rate"] = price_data["purchase_rate"].apply(lambda x: "-" if pd.isna(x) else f"{x}%")
    price_data["jeonse_rate"] = price_data["jeonse_rate"].apply(lambda x: "-" if pd.isna(x) else f"{x}%")
    
    price_data.columns = ["구분", "매매가평균", "전세가평군", "매매건수", "전세건수", "매매가상승률(%)", "전세가상승률(%)"]

    print(price_data)

    # 최고 매매가 및 전세가 계산
    max_purchase = df.loc[df['price'].idxmax()] if not df.empty else None
    max_jeonse = df_1.loc[df_1['price'].idxmax()] if not df_1.empty else None

    if max_purchase is not None:
        max_purchase_date = max_purchase['date'].strftime('%Y-%m-%d')
        max_purchase_price = round(max_purchase['price'] / 10000, 1)
    else:
        max_purchase_date = "-"
        max_purchase_price = "-"

    if max_jeonse is not None:
        max_jeonse_date = max_jeonse['date'].strftime('%Y-%m-%d')
        max_jeonse_price = round(max_jeonse['price'] / 10000, 1)
    else:
        max_jeonse_date = "-"
        max_jeonse_price = "-"

    # 테이블 데이터를 HTML로 변환
    table_html = price_data.to_html(classes="table table-striped", index=False)

    # 최고가 강조 정보
    max_info_html = f"""
    <p><b>최고 매매가:</b> {max_purchase_price}억 ({max_purchase_date})</p>
    <p><b>최고 전세가:</b> {max_jeonse_price}억 ({max_jeonse_date})</p>
    """

    # 산점도 그리기
    plt.figure(figsize=(10, 6))
    plt.scatter(df['date'], df['price'], alpha=0.5, label='Purchase')
    plt.scatter(df_1['date'], df_1['price'], alpha=0.5, label='Jeonse')

    # 최고 매매가와 전세가 강조
    if max_purchase is not None:
        plt.scatter(max_purchase['date'], max_purchase['price'], color='red', label='Max Purchase Price', s=100, edgecolor='black', zorder=5)
    if max_jeonse is not None:
        plt.scatter(max_jeonse['date'], max_jeonse['price'], color='blue', label='Max Jeonse Price', s=100, edgecolor='black', zorder=5)

    plt.title('연도별 매매-전세 가격분포')

    plt.legend()

    # 이미지 저장
    buf = BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    img_str = base64.b64encode(buf.getvalue()).decode('utf-8')
    buf.close()

    # 사용승인 연수 계산
    current_year = datetime.now().year
    useApproveYmd = int(apt_list_instance.useApproveYmd)
    d_year = current_year - useApproveYmd + 1

    # context에 데이터 전달
    context = {
        'apt_list': apt_list_instance,
        'apt_detail': apt_detail_instance,
        'details': details,
        'img_str': img_str,
        'table_html': table_html,
        'max_info_html': max_info_html,
        'd_year': d_year,
        'latitude': apt_list_instance.latitude,
        'longitude': apt_list_instance.longitude,
    }

    return render(request, 'apt_detail.html', context)
