# Status/views.py
from django.shortcuts import render, get_object_or_404
from home.models import Division, District, Upazila, Union, Ward, Housh


def status(request):
    floody_divisions = Division.objects.filter(
        district__upazila__union__ward__is_flood=True
    ).distinct()
    return render(request, 'status/status.html', {'floody_divisions': floody_divisions})


def district_status(request, division_id):
    division = get_object_or_404(Division, id=division_id)
    floody_districts = District.objects.filter(
        division=division,
        upazila__union__ward__is_flood=True
    ).distinct()
    return render(request, 'status/district_status.html', {
        'division': division,
        'districts': floody_districts,
    })


def upazila_status(request, district_id):
    district = get_object_or_404(District, id=district_id)
    floody_upazilas = Upazila.objects.filter(
        district=district,
        union__ward__is_flood=True
    ).distinct()
    return render(request, 'status/upazila_status.html', {
        'district': district,
        'upazilas': floody_upazilas,
    })


def union_status(request, upazila_id):
    upazila = get_object_or_404(Upazila, id=upazila_id)
    floody_unions = Union.objects.filter(
        upazila=upazila,
        ward__is_flood=True
    ).distinct()
    return render(request, 'status/union_status.html', {
        'upazila': upazila,
        'unions': floody_unions,
    })


def ward_status(request, union_id):
    union = get_object_or_404(Union, id=union_id)
    flooded_wards = Ward.objects.filter(union=union, is_flood=True)
    return render(request, 'status/ward_status.html', {
        'union': union,
        'wards': flooded_wards,
    })


def house_status(request, ward_id):
    ward = get_object_or_404(Ward, id=ward_id)
    houses = Housh.objects.filter(ward=ward)
    return render(request, 'status/house_status.html', {
        'ward': ward,
        'houses': houses,
    })
