from django.db import models
from apt.models import Apt_list, Location


class City(models.Model):
    city_name = models.CharField(max_length=20, verbose_name = "도시이름")
    city_code = models.CharField(max_length=20, unique=True, verbose_name="도시코드")

class District(models.Model):
    district_name = models.CharField(max_length=20, verbose_name = "시군구이름")
    district_code = models.CharField(max_length=20, unique=True, verbose_name="시군구코드")
    city_code = models.ForeignKey(
        'City',
        on_delete=models.CASCADE,
        to_field = "city_code", 
        db_column="city_code",
        verbose_name="도시코드",
    )

class Neighborhood(models.Model):
    neighborhood_name = models.CharField(max_length=20, verbose_name = "시군구이름")
    district_code = models.ForeignKey(
        'District',
        on_delete=models.CASCADE,
        to_field = "district_code", 
        db_column="district_code",
        verbose_name="시군구코드",
        related_name="neighborhoods"
    )
    location_code = models.ForeignKey(
        Location,
        on_delete=models.CASCADE,
        to_field = "cortarNo", 
        db_column= "neighborhood_code",
        verbose_name="읍면동코드",
        related_name="neighborhoods"

    )


# class Neighborhood(models.Model):
#     neighborhood_name = models.CharField(max_length=20)
#     district_code = models.ForeignKey(  # ✅ district_code → district 로 변경
#         District,
#         on_delete=models.CASCADE,
#         db_column="district_code",
#         verbose_name="시군구",
#     )
#     neighborhood_code = models.ForeignKey(
#         Location,
#         on_delete=models.CASCADE,
#         to_field='cortarNo',
#         db_column='neighborhood_code',
#         verbose_name="읍면동코드",

#     )
