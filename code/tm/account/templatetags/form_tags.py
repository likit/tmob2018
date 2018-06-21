from django.template import Library, loader
from django.urls import resolve

register = Library()

@register.filter(name="add_css")
def add_css(field, css):
    return field.as_widget(attrs={"class": css})