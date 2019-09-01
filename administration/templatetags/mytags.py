from django import template

register = template.Library()

@register.filter
def typeConvert(value:int):
    switcher={
        1:'Morring',
        2:'Afternoon',
        3:'Evenning',
        4:'On Call',
        5:'Sleep',
        6:'OFF Day',
    }

    return switcher.get(value)