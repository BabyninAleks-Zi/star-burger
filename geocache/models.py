from django.db import models


class AddressCache(models.Model):
    address = models.CharField(
        'адрес',
        max_length=500,
        unique=True,
    )
    latitude = models.FloatField(
        'широта',
    )
    longitude = models.FloatField(
        'долгота',
    )
    geocoded_at = models.DateTimeField(
        'дата запроса к геокодеру',
        db_index=True,
    )

    class Meta:
        verbose_name = 'кэш адреса'
        verbose_name_plural = 'кэш адресов'

    def __str__(self):
        return self.address
