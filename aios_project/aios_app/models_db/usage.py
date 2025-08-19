from django.db import models
from django.conf import settings
from django.utils import timezone
from django.core.validators import MinValueValidator


class Usage(models.Model):
    # Input types
    TYPE_FERTILIZER = "fertilizer"
    TYPE_PESTICIDE  = "pesticide"
    TYPE_SEED       = "seed"
    INPUT_TYPES = [
        (TYPE_FERTILIZER, "Fertilizer"),
        (TYPE_PESTICIDE,  "Pesticide"),
        (TYPE_SEED,       "Seed"),
    ]

    # Units
    UNIT_KG    = "kg"
    UNIT_LITER = "l"
    UNIT_PCS   = "pcs"
    UNITS = [
        (UNIT_KG, "kg"),
        (UNIT_LITER, "liters"),
        (UNIT_PCS, "pieces"),
    ]

    # Who/where
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="input_usages",
    )
    crop = models.CharField(max_length=100, blank=True, null=True)
    field_name = models.CharField(max_length=100, blank=True, null=True)

    # What
    input_type = models.CharField(max_length=20, choices=INPUT_TYPES)
    product_name = models.CharField(max_length=150)
    brand = models.CharField(max_length=150, blank=True, null=True)

    # How much
    quantity = models.DecimalField(
        max_digits=12, decimal_places=2,
        validators=[MinValueValidator(0.01)]
    )
    unit = models.CharField(max_length=10, choices=UNITS)
    cost = models.DecimalField(
        max_digits=12, decimal_places=2, blank=True, null=True,
        validators=[MinValueValidator(0)]
    )

    # When (season)
    season_year = models.PositiveIntegerField()         # e.g., 2025
    season_name = models.CharField(max_length=30)       # e.g., "Season A", "Season B"
    application_date = models.DateField(default=timezone.now)

    # Notes
    notes = models.TextField(blank=True, null=True)

    # Meta
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["farmer", "season_year", "season_name"]),
            models.Index(fields=["input_type", "application_date"]),
        ]
        ordering = ["-application_date", "-created_at"]
        verbose_name = "Input usage"
        verbose_name_plural = "Input usages"

    def __str__(self):
        return f"{self.farmer} • {self.input_type} • {self.product_name} ({self.season_year} {self.season_name})"