import os
from typing import Dict, TypedDict, List
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.http import HttpResponse, JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from django.conf import settings
import pyproj
import requests
from haversine import haversine
from enum import Enum
import json
import asyncio


def iterate_data_generator(operateurs_data):
    for op_data in operateurs_data:
        yield op_data


def read_csv_file_in_memory():
    filePath = os.path.join(
        settings.BASE_DIR,
        "network",
        "raw_network_coverage_data.csv",
    )
    outputPath = os.path.join(
        settings.BASE_DIR,
        "network",
        "output.json",
    )

    df = pd.read_csv(filePath)
    csv_data = df.to_dict(orient="records")
    return csv_data


class AddressInfo(TypedDict):
    address: str
    longitude: float
    latitude: float


class Operator(Enum):
    ORANGE = "orange"
    SFR = "sfr"
    BOUYGUES = "bouygues"
    FREE = "free"


class OperatorTech(Enum):
    G2 = "2G"
    G3 = "3G"
    G4 = "4G"


CoverageOfOneAddressInfo = Dict[Operator, Dict[OperatorTech, bool]]

coverage_tech_range = {"2G": 30, "3G": 5, "4G": 10}  # unit: km
operators: List[str] = [item.value for item in Operator]
network_coverage_data = read_csv_file_in_memory()
slice_network_coverage_data = network_coverage_data[:500]


def lamber93_to_gps(x, y):
    lambert = pyproj.Proj(
        "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
    )
    wgs84 = pyproj.Proj("+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs")
    x = 102980
    y = 6847973
    long, lat = pyproj.transform(lambert, wgs84, x, y)
    return long, lat


def get_addresse_info_from_gov_api(key: str, address: str) -> AddressInfo:
    print("new sync call", key)
    url = f"https://api-adresse.data.gouv.fr/search/?q={address}&limit=1"

    response = requests.get(url)
    data = response.json()

    return {
        "address": data.get("query"),
        "longitude": data.get("features")[0].get("geometry").get("coordinates")[0],
        "latitude": data.get("features")[0].get("geometry").get("coordinates")[1],
    }


async def get_addresse_info_from_gov_api_async(key: str, address: str) -> AddressInfo:
    print("new async call", key)
    url = f"https://api-adresse.data.gouv.fr/search/?q={address}&limit=1"

    response = requests.get(url)
    data = response.json()

    return {
        "address": data.get("query"),
        "longitude": data.get("features")[0].get("geometry").get("coordinates")[0],
        "latitude": data.get("features")[0].get("geometry").get("coordinates")[1],
    }


def check_coverage(
    operators_info: List[any], address_info: AddressInfo, coverage_tech_range
):
    coverage_info_for_address: CoverageOfOneAddressInfo = {
        item: {
            "2G": False,
            "3G": False,
            "4G": False,
        }
        for item in operators
    }
    address_query = address_info["address"]
    address_coord = (address_info["longitude"], address_info["latitude"])

    for operator_data in iterate_data_generator(operators_info):
        operator_name = operator_data["Operateur"].lower()
        allCovered_for_operator = all(
            value == True for value in coverage_info_for_address[operator_name].values()
        )
        if allCovered_for_operator:
            continue

        long, lat = lamber93_to_gps(operator_data.get("x"), operator_data.get("y"))
        operator_data["longitude"] = long
        operator_data["latitude"] = lat

        operator_coord = (operator_data["longitude"], operator_data["latitude"])
        distance = haversine(address_coord, operator_coord, unit="km")

        for tech in coverage_tech_range.keys():
            isCovered: bool = (
                distance <= coverage_tech_range[tech]
                if operator_data[tech] == True
                else False
            )
            if isCovered:
                coverage_info_for_address[operator_name][tech] = True

    yield address_query, coverage_info_for_address


def process_one_address(
    coverage_result_for_one_address: Dict[str, CoverageOfOneAddressInfo],
    key: str,
    values: str,
):
    address_info: AddressInfo = get_addresse_info_from_gov_api(key, values)

    for address_query, coverage_info in check_coverage(
        slice_network_coverage_data, address_info, coverage_tech_range
    ):
        coverage_result_for_one_address[address_query] = coverage_info

    return coverage_result_for_one_address


async def process_one_address_async(
    coverage_result_for_one_address: Dict[str, CoverageOfOneAddressInfo],
    key: str,
    values: str,
):
    address_info: AddressInfo = await get_addresse_info_from_gov_api_async(key, values)

    for address_query, coverage_info in check_coverage(
        slice_network_coverage_data, address_info, coverage_tech_range
    ):
        coverage_result_for_one_address[address_query] = coverage_info

    return coverage_result_for_one_address


@api_view(["POST"])
def network_recoverage_messaure(request):
    try:
        address_info: Dict[str, str] = request.data

        coverage_result: Dict[str, CoverageOfOneAddressInfo] = {}

        for key, values in address_info.items():
            process_one_address(coverage_result, key, values)

        return Response(coverage_result)

    except Exception as e:
        print(f"Error occurred: {e}")
        return Response({"error": "An error occurred"}, status=500)


@csrf_exempt
async def network_recoverage_messaure_async(request):
    try:

        address_info: Dict[str, str] = json.loads(request.body.decode("utf-8"))

        coverage_result: Dict[str, CoverageOfOneAddressInfo] = {}

        tasks = [
            process_one_address_async(coverage_result, key, values)
            for key, values in address_info.items()
        ]

        results = await asyncio.gather(*tasks)

        for result in results:
            coverage_result.update(result)

        return JsonResponse(coverage_result)

    except Exception as e:
        print(f"Error occurred: {e}")
        return HttpResponse({"error": "An error occurred"}, status=500)
