import os
import django
import pandas as pd
from pathlib import Path
from tqdm import tqdm

import pandas as pd
import numpy as np
import requests
import json
import time


import sqlite3



headers = {
"Accept-Encoding": "gzip, deflate, br",
"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IlJFQUxFU1RBVEUiLCJpYXQiOjE2NTk5MzcxNTIsImV4cCI6MTY1OTk0Nzk1Mn0.PD7SqZO7z8f97uGQpfSKYMPbrLy6YtRl9XYHWaHiVVE",
"Host": "new.land.naver.com",
"Referer": "https://new.land.naver.com/...",
# "sec-ch-ua": "\".Not\/A)Brand\";v=\"99\", \"Google Chrome\";v=\"103\", \"Chromium\";v=\"103\"",
"sec-ch-ua-mobile": "?0",
"sec-ch-ua-platform": "macOS",
"Sec-Fetch-Dest": "empty",
"Sec-Fetch-Mode": "cors",
"Sec-Fetch-Site": "same-origin",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36"
}

# Django 설정
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "_prj.settings")
django.setup()

# BASE_DIR 설정 (settings.py에서 가져오는 방식과 동일)
BASE_DIR = Path(__file__).resolve().parent.parent

def data_update():
    try:
    # 1) 네이버 기준의 시도 코드 확보    
        down_url = 'https://new.land.naver.com/api/regions/list?cortarNo=0000000000'
        r = requests.get(down_url,data={"sameAddressGroup":"false"},headers=headers)
        r.encoding = "utf-8-sig"
        temp=json.loads(r.text)
        sido = pd.DataFrame(temp["regionList"])        
        sido.columns = ['sido_list', 'centerLat', 'centerLon', 'sido_name', 'cortarType']
        sido_list = []
        sido_name =[]

        for i in range(len(temp["regionList"])):
            sido_list.append(temp['regionList'][i]['cortarNo'])
            sido_name.append(temp['regionList'][i]['cortarName'])


    # 2) 네이버 기준의 시도 코드에 속한 하위코드 추출
        gu_sido = []
        gu_gu = []
        gu_name = []

        for i in range(len(sido)):
            down_url = 'https://new.land.naver.com/api/regions/list?cortarNo='+sido_list[i]
            r = requests.get(down_url,data={"sameAddressGroup":"false"},headers=headers)
            r.encoding = "utf-8-sig"
            temp = json.loads(r.text)
            for j in range(len(temp["regionList"])):
                gu_sido.append(sido["sido_list"][i])
                gu_gu.append(temp['regionList'][j]['cortarNo'])
                gu_name.append(temp['regionList'][j]['cortarName'])

        gu_region = pd.DataFrame({"gu_sido" : gu_sido,  
                          "gu_gu" : gu_gu,
                          "gu_name" : gu_name})
        print(gu_region)
    # 3)네이버 기준의 구군 코드에 하위 속한 하위코드 추출


        dong_si = []
        dong_gu = []
        dong_dong =[]
        dong_name = []

        for i in tqdm(range(len(gu_region))):
            down_url = 'https://new.land.naver.com/api/regions/list?cortarNo='+gu_region["gu_gu"][i]
            r = requests.get(down_url,data={"sameAddressGroup":"false"},headers=headers)
            r.encoding = "utf-8-sig"
            temp = json.loads(r.text)
            for j in range(len(temp["regionList"])):
                dong_si.append(gu_region["gu_sido"][i])
                dong_gu.append(gu_region["gu_gu"][i])
                dong_dong.append(temp['regionList'][j]['cortarNo'])
                dong_name.append(temp['regionList'][j]['cortarName'])
            time.sleep(.1)

        dong_region = pd.DataFrame({"dong_si":dong_si,
                                "dong_gu":dong_gu,                             
                                "dong_dong" : dong_dong, 
                                "dong_name": dong_name})
        print(dong_region)

    # 4) 전국아파트리스트_업데이트_갱신
        apt_si = []
        apt_gu = []
        apt_dong = []
        apt_info = []


        for i in tqdm(range(len(dong_region))):
            down_url = 'https://new.land.naver.com/api/regions/complexes?cortarNo='+ dong_region["dong_dong"][i] +'&realEstateType=APT:ABYG:JGC:JGB&order='
            r = requests.get(down_url,data={"sameAddressGroup":"false"},headers=headers)
            r.encoding = "utf-8-sig"
            temp = json.loads(r.text)
            for j in range(len(temp["complexList"])):
                apt_si.append(dong_region["dong_si"][i])
                apt_gu.append(dong_region["dong_gu"][i])
                apt_dong.append(dong_region["dong_dong"][i])
                apt_info.append(temp["complexList"][j])
            time.sleep(.1)

        new_apt_list=pd.DataFrame(apt_info)
        
        print(new_apt_list.head())

# sqlite3 db 접속해서 기존정보 가져오기
        conn = sqlite3.connect("db.sqlite3")  # 'real.db'는 SQLite 데이터베이스 파일 이름
        cursor = conn.cursor()

        # 데이터 조회
        query = "SELECT * FROM apt_apt_list"
        cursor.execute(query)

        # 데이터 가져오기
        db_export = cursor.fetchall()

        # 컬럼명 가져오기
        columns = [desc[0] for desc in cursor.description]

        # Pandas 데이터프레임으로 변환
        old_apt_base = pd.DataFrame(db_export, columns=columns)

        # 연결 종료
        conn.close()

        # 데이터 확인
        print(old_apt_base.head())

        new_list = new_apt_list[~new_apt_list['complexNo'].isin(old_apt_base['complexNo'])]["complexNo"]

# 새로운 아파트 정보만 크롤링 하기
        new_apt_info = []
    
        for list in tqdm(new_list):
            down_url = 'https://new.land.naver.com/api/complexes/'+list+'?sameAddressGroup=false'
            r = requests.get(down_url,data={"sameAddressGroup":"false"},headers=headers)
            r.encoding = "utf-8-sig"
            temp=json.loads(r.text)
            new_apt_info.append(temp)
            time.sleep(.1)

        data_1 = [] 
        data_2 = []
        imageKey = []
        smallCategoryName = []
        imageSrc = []
        imageId  = []
        explanation = []
        
        for data in new_apt_info:
            comno = data['complexDetail']['complexNo']
            data_1.append(data["complexDetail"])
            for i in range(len(data["complexPyeongDetailList"])):
                type = data["complexPyeongDetailList"][i]
                type["complexNo"] = comno
                data_2.append(type)
            
            for photo in data["photos"]:
                try:
                    imageKey.append(photo["imageKey"])
                    smallCategoryName.append(photo["smallCategoryName"])
                    imageSrc.append("https://landthumb-phinf.pstatic.net" + photo["imageSrc"])
                    imageId.append(photo["imageId"])
                    explanation.append(photo["explaination"])

                except:
                    explanation.append("")
                    
        new_apt_photo = pd.DataFrame({"imageKey" : imageKey,
                      "smallCategoryName" : smallCategoryName,
                      "imageSrc" : imageSrc,
                      "imageId"  : imageId,
                      "explanation" : explanation})

# 새롭게 취득된 apt_list 정보를 DB에 추가하기
## 데이터정리
        new_apt_base = pd.DataFrame(data_1)
        new_apt_base = new_apt_base[[
                                    "complexNo", 
                                    "complexName", 
                                    "roadAddressPrefix", 
                                    "roadAddress",
                                    "address",
                                    "detailAddress",
                                    "totalDongCount",
                                    "maxSupplyArea",
                                    "minSupplyArea",
                                    "parkingCountByHousehold",
                                    "parkingPossibleCount",                   
                                    "totalHouseholdCount", 
                                    "totalLeaseHouseholdCount", 
                                    "useApproveYmd",
                                    "latitude",
                                    "longitude",
                                    "cortarNo"
                                    ]]
        # new_apt_base["cortarNo"] = new_apt_base["cortarNo"].map(lambda x : x[:5])
        # new_apt_base["cortarNo"] = new_apt_base["cortarNo"].map(lambda x: x + "00000" if x not in ['50110', '50130'] else "5000000000")
        new_apt_base["useApproveYmd"] = new_apt_base["useApproveYmd"].astype(str)
        new_apt_base["useApproveYmd"] = new_apt_base["useApproveYmd"].map(lambda x: x[:4] if x != 'nan' else x) 
        new_apt_base["roadAddress"]= new_apt_base["roadAddress"].map(lambda x: "-" if pd.isna(x) else x)

        new_apt_base = new_apt_base.where(pd.notnull(new_apt_base), None)


# 새롭게 취득된 apt_list 정보를 DB에 추가하기
        # SQLite 연결
        conn = sqlite3.connect("db.sqlite3")  # 'real.db'는 SQLite 데이터베이스 파일명
        cursor = conn.cursor()

        # INSERT OR IGNORE 쿼리
        insert_query = """
        INSERT or IGNORE INTO apt_apt_list 
            (complexNo, 
            complexName, 
            roadAddressPrefix, 
            roadAddress, 
            address, 
            detailAddress, 
            totalDongCount, 
            maxSupplyArea, 
            minSupplyArea, 
            parkingCountByHousehold, 
            parkingPossibleCount, 
            totalHouseholdCount, 
            totalLeaseHouseholdCount, 
            useApproveYmd, 
            latitude, 
            longitude, 
            cortarNo) 
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # 데이터를 튜플로 변환하여 삽입
        data_tuples = [tuple(row) for row in new_apt_base.values]
        cursor.executemany(insert_query, data_tuples)

        # 커밋 및 연결 닫기
        conn.commit()
        conn.close()

# 새롭게 취득된 apt_detail 정보를 DB에 추가하기
## 데이터정리
        new_apt_base_detail = pd.DataFrame(data_2)
        new_apt_base_detail = new_apt_base_detail[['pyeongNo', 
                                   'supplyAreaDouble', 
                                   'pyeongName',
                                   'exclusiveArea', 
                                   'householdCountByPyeong',  
                                   'entranceType', 
                                   'roomCnt', 
                                   'bathroomCnt', 
                                   'complexNo']]
        new_apt_base_detail["complexno_py"] = new_apt_base_detail["complexNo"] + "_" + new_apt_base_detail["pyeongNo"]


# 새롭게 취득된 apt_detail 정보를 DB에 추가하기

        # SQLite 연결
        conn = sqlite3.connect("db.sqlite3")  # 'real.db'는 SQLite 데이터베이스 파일명
        cursor = conn.cursor()


        # INSERT OR IGNORE 쿼리
        insert_query = """
        INSERT OR IGNORE INTO apt_apt_detail 
                (pyeongNo,
                supplyAreaDouble,
                pyeongName,
                exclusiveArea,
                householdCountByPyeong,
                entranceType,
                roomCnt,
                bathroomCnt,
                complexNo,
                complexno_py)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """

        # 데이터를 튜플로 변환하여 삽입
        data_tuples = [tuple(row) for row in new_apt_base_detail.values]
        cursor.executemany(insert_query, data_tuples)

        # 커밋 및 연결 닫기
        conn.commit()
        conn.close()

    except Exception as e:
        print("Error occurred:", e)



# 새롭게 취득된 apt_apt_photo 정보를 DB에 추가하기

        # SQLite 연결
        conn = sqlite3.connect("db.sqlite3")  # 'real.db'는 SQLite 데이터베이스 파일명
        cursor = conn.cursor()


        # INSERT OR IGNORE 쿼리
        insert_query = """
        INSERT OR IGNORE INTO apt_apt_photo 
                (imageKey,
                smallCategoryName,
                imageSrc,
                imageId,
                explanation)
        VALUES (?, ?, ?, ?, ?)
        """

        # 데이터를 튜플로 변환하여 삽입
        data_tuples = [tuple(row) for row in new_apt_photo.values]
        cursor.executemany(insert_query, data_tuples)

        # 커밋 및 연결 닫기
        conn.commit()
        conn.close()

    except Exception as e:
        print("Error occurred:", e)


if __name__ == "__main__":
    data_update()
