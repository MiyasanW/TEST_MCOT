from django import template
from rentals.models import Product

register = template.Library()

@register.filter
def get_category_label(value):
    """
    Returns the display label for a given category key.
    Usage: {{ product.category|get_category_label }}
    """
    for key, label in Product.CATEGORY_CHOICES:
        if key == value:
            return label
    return value
