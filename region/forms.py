from django import forms
from .models import City, District, Neighborhood

class LocationForm(forms.Form):
    city = forms.ModelChoiceField(
        queryset=City.objects.all(),
        empty_label="도시 선택",
        required=True
    )
    district = forms.ModelChoiceField(
        queryset=District.objects.none(),  # 초기에는 비워둠
        empty_label="구 선택",
        required=True
    )
    neighborhood = forms.ModelChoiceField(
        queryset=Neighborhood.objects.none(),  # 초기에는 비워둠
        empty_label="동 선택",
        required=True
    )

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)
    #     if "city" in self.data:
    #         try:
    #             city_code = self.data.get("city")
    #             print(city_code)
    #             self.fields["district_code"].queryset = District.objects.filter(city_code=city_code)
    #         except (ValueError, TypeError):
    #             pass  # 데이터가 올바르지 않으면 비워둠

    #     if "district" in self.data:
    #         try:
    #             district_code = self.data.get("district")
    #             self.fields["neighborhood_code"].queryset = Neighborhood.objects.filter(district_code=district_code)
    #         except (ValueError, TypeError):
    #             pass
