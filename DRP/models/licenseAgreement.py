"""A module containing only the LicenseAgreement class."""
from django.db import models
from django.contrib import auth
from .license import License


class LicenseAgreement(models.Model):
    """The LicenseAgreement class details the date and time a license was agreed to by a user."""

    class Meta:
        app_label = "DRP"

    user = models.ForeignKey(auth.models.User, on_delete=models.PROTECT)
    text = models.ForeignKey(License, on_delete=models.PROTECT)
    signedDateTime = models.DateTimeField(auto_now=True)
