from django.conf import settings
from django.utils import timezone

import requests
from requests.exceptions import RequestException

from .models import AddressCache


def fetch_coordinates(apikey, address):
    geocoder_url = 'https://geocode-maps.yandex.ru/1.x'
    response = requests.get(
        geocoder_url,
        params={
            'apikey': apikey,
            'geocode': address,
            'format': 'json',
        },
        timeout=5,
    )
    response.raise_for_status()

    found_places = response.json()['response']['GeoObjectCollection']['featureMember']
    if not found_places:
        return None

    longitude, latitude = found_places[0]['GeoObject']['Point']['pos'].split(' ')
    return float(latitude), float(longitude)


def get_coordinates_by_address(addresses):
    if not addresses:
        return {}

    cached_addresses = AddressCache.objects.filter(address__in=addresses)
    cached_by_address = {
        cache_item.address: cache_item
        for cache_item in cached_addresses
    }

    coordinates_by_address = {
        address: (cache_item.latitude, cache_item.longitude)
        for address, cache_item in cached_by_address.items()
    }

    stale_before = timezone.now() - settings.GEOCODER_CACHE_TTL
    addresses_to_refresh = [
        address
        for address, cache_item in cached_by_address.items()
        if cache_item.geocoded_at < stale_before
    ]
    addresses_to_create = [address for address in addresses if address not in cached_by_address]
    addresses_to_fetch = addresses_to_create + addresses_to_refresh

    geocoder_api_key = settings.YANDEX_GEOCODER_API_KEY
    if not geocoder_api_key or not addresses_to_fetch:
        return coordinates_by_address

    new_cache_items = []
    changed_cache_items = []
    for address in addresses_to_fetch:
        try:
            coordinates = fetch_coordinates(geocoder_api_key, address)
        except (RequestException, KeyError, ValueError, TypeError):
            continue

        if coordinates is None:
            continue

        latitude, longitude = coordinates
        coordinates_by_address[address] = (latitude, longitude)

        cached_item = cached_by_address.get(address)
        if cached_item is None:
            new_cache_items.append(AddressCache(
                address=address,
                latitude=latitude,
                longitude=longitude,
                geocoded_at=timezone.now(),
            ))
            continue

        cached_item.latitude = latitude
        cached_item.longitude = longitude
        cached_item.geocoded_at = timezone.now()
        changed_cache_items.append(cached_item)

    if new_cache_items:
        AddressCache.objects.bulk_create(new_cache_items, ignore_conflicts=True)
    if changed_cache_items:
        AddressCache.objects.bulk_update(
            changed_cache_items,
            ['latitude', 'longitude', 'geocoded_at'],
        )

    return coordinates_by_address
