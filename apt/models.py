from django.db import models


class Location(models.Model):
    name = models.CharField(max_length=100, verbose_name="지역명")
    cortarNo = models.CharField(max_length=10, unique=True, verbose_name="해당지역코드")  # unique 추가

    class Meta:
        verbose_name = "기준지역"
        verbose_name_plural = "기준지역 목록"
        ordering = ['cortarNo']

    # def __str__(self):
    #     return f"{self.name} ({self.cortarNo})"

class Apt_list(models.Model):
    complexNo = models.CharField("단지번호", max_length=10, unique=True)  # 단지번호를 고유값으로 설정
    cortarNo = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        to_field='cortarNo', 
        db_column='cortarNo', 
        verbose_name="법정동코드",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )  # Location 모델을 참조하는 외래키로 변경
    complexName = models.CharField("단지명", max_length=30)
    roadAddressPrefix = models.CharField("도로명_1", max_length=20)
    roadAddress = models.CharField("도로명_2", max_length=20)
    address = models.CharField("주소_1", max_length=20)
    detailAddress = models.CharField("주소_2", max_length=20)
    totalDongCount = models.PositiveIntegerField("전체동수")
    maxSupplyArea = models.DecimalField("최대공급면적", max_digits=5, decimal_places=1)
    minSupplyArea = models.DecimalField("최소공급면적", max_digits=5, decimal_places=1)
    parkingCountByHousehold = models.DecimalField("세대당주차대수", max_digits=3, decimal_places=1)
    parkingPossibleCount = models.PositiveIntegerField("세대수")
    totalHouseholdCount = models.PositiveIntegerField("세대수")
    totalLeaseHouseholdCount = models.PositiveIntegerField("임대세대수")
    useApproveYmd = models.CharField("준공일", max_length=30)
    latitude = models.DecimalField("위도", max_digits=10, decimal_places=6)
    longitude = models.DecimalField("경도", max_digits=10, decimal_places=6)

    def __str__(self):
        return self.complexName

    class Meta:
        verbose_name = "아파트 단지"
        verbose_name_plural = "아파트 단지 목록"
        ordering = ['complexName']

class Apt_detail(models.Model):
    pyeongNo = models.CharField("평형번호", max_length=10)
    supplyAreaDouble = models.DecimalField("공급면적", max_digits=10, decimal_places=6)
    pyeongName = models.CharField("평이름", max_length=10)
    exclusiveArea = models.DecimalField("전용면적", max_digits=10, decimal_places=6)
    householdCountByPyeong = models.PositiveIntegerField("세대수")
    entranceType = models.CharField("계단/복도형", max_length=10)
    roomCnt = models.CharField("방수", max_length=10)
    bathroomCnt = models.CharField("욕실수", max_length=10)
    complexno_py = models.CharField("단지번호_평형", max_length=10, unique=True, default="DEFAULT")

    # 외래 키 설정
    complexNo = models.ForeignKey(
        'Apt_list', 
        on_delete=models.CASCADE, 
        to_field='complexNo', 
        db_column='complexNo', 
        verbose_name="단지번호" 
    )

    def __str__(self):
        return f"{self.complexNo.complexName} - {self.pyeongName}"

    class Meta:
        verbose_name = "아파트 상세"
        verbose_name_plural = "아파트 상세 목록"


class Apt_current(models.Model):
    date = models.CharField("기준일", max_length=10)
    price = models.PositiveIntegerField("매매가")
    jeonse = models.PositiveIntegerField("전세가")

    # 외래 키 설정
    complexNo = models.ForeignKey(
        'Apt_list',
        on_delete=models.CASCADE,
        to_field='complexNo',
        db_column='complexNo',
        verbose_name="단지번호"
    )

    complexno_py = models.ForeignKey(
        'Apt_detail',
        on_delete=models.CASCADE,
        to_field='complexno_py',
        db_column='complexno_py',
        verbose_name="평형 상세",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

    def __str__(self):
        return f"{self.complexNo.complexName} - {self.complexno_py.pyeongName} - {self.date } - {self.price}만원"

    class Meta:
        verbose_name = "아파트 거래 상세"
        verbose_name_plural = "아파트 거래 상세 목록"
        verbose_name = "아파트 거래 상세"
        verbose_name_plural = "아파트 거래 상세 목록"


class Apt_purchase(models.Model):
    date = models.CharField("거래일", max_length=10)
    price = models.PositiveIntegerField("매매가")

    # 외래 키 설정
    complexNo = models.ForeignKey(
        'Apt_list',
        on_delete=models.CASCADE,
        to_field='complexNo',
        db_column='complexNo',
        verbose_name="단지번호"
    )

    complexno_py = models.ForeignKey(
        'Apt_detail',
        on_delete=models.CASCADE,
        to_field='complexno_py',
        db_column='complexno_py',
        verbose_name="평형 상세",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

    def __str__(self):
        return f"{self.complexNo.complexName} - {self.complexno_py.pyeongName} - {self.date } - {self.price}만원"

    class Meta:
        verbose_name = "아파트 거래 상세"
        verbose_name_plural = "아파트 거래 상세 목록"
        verbose_name = "아파트 거래 상세"
        verbose_name_plural = "아파트 거래 상세 목록"

class Apt_jeonse(models.Model):
    date = models.CharField("거래일", max_length=10)
    price = models.PositiveIntegerField("전세가")

    # 외래 키 설정
    complexNo = models.ForeignKey(
        'Apt_list',
        on_delete=models.CASCADE,
        to_field='complexNo',
        db_column='complexNo',
        verbose_name="단지번호"
    )

    complexno_py = models.ForeignKey(
        'Apt_detail',
        on_delete=models.CASCADE,
        to_field='complexno_py',
        db_column='complexno_py',
        verbose_name="평형 상세",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

    def __str__(self):
        return f"{self.complexNo.complexName} - {self.complexno_py.pyeongName} - {self.date } - {self.price}만원"

    class Meta:
        verbose_name = "아파트 전세 상세"
        verbose_name_plural = "아파트 전세 상세 목록"
        verbose_name = "아파트 전세 상세"
        verbose_name_plural = "아파트 전세 상세 목록"

class Apt_ratio(models.Model):
    max_price = models.PositiveIntegerField("최고가", null=True, blank=True, default=0.0)
    current_price = models.PositiveIntegerField("최근거래가", null=True, blank=True, default=0.0)
    current_jeonse = models.PositiveIntegerField("최근전세가", null=True, blank=True, default=0.0)
    by_max = models.FloatField("최고가대비", null=True, blank=True, default=0.0)
    by_jeonse = models.FloatField("전세가대비", null=True, blank=True, default=0.0)

    # 외래 키 설정
    complexNo = models.ForeignKey(
        'Apt_list',
        on_delete=models.SET_NULL,
        to_field='complexNo',
        db_column='complexNo',
        verbose_name="단지번호",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

    complexno_py = models.ForeignKey(
        'Apt_detail',
        on_delete=models.SET_NULL,
        to_field='complexno_py',
        db_column='complexno_py',
        verbose_name="평형 상세",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

class Apt_jisu(models.Model):
    date = models.CharField("거래월", max_length=10)
    jisu = models.FloatField("kb매매지수", null=True, blank=True)
    jeonse_jisu = models.FloatField("kb전세지수", null=True, blank=True)

    # 외래 키 설정
    cortarNo = models.ForeignKey(
        'Location',
        on_delete=models.SET_NULL,
        to_field='cortarNo',  # 'cortarNo' 필드를 참조
        db_column='cortarNo',  # DB에서 컬럼명 설정
        verbose_name="지역명",
        null=True,  # 비어 있는 값을 허용
        blank=True  # 관리 페이지에서 빈 값 허용
    )

    def __str__(self):
        return f"{self.location.name} - {self.date} - {self.jisu}"

    class Meta:
        verbose_name = "아파트 지수"
        verbose_name_plural = "아파트 지수 목록"


class Apt_photo(models.Model):
    imageKey = models.CharField("단지번호", max_length=10)
    smallCategoryName = models.CharField("사진설명", max_length=10, null = True)
    imageSrc = models.CharField("이미지_원본", max_length=300)
    imageId = models.CharField("이미지_아이디", max_length=100)
    explaination = models.TextField("사진설명", null = True)
