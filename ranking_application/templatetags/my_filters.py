from django.template.defaultfilters import register
import decimal

@register.filter(name='lookup')
def lookup(dict, index):
    if index in dict:
        return dict[index]
    return ''

@register.filter
def check_empty(dictionary):
    for elem in dictionary:
        if dictionary[elem]:
            return True
    return False

@register.filter
def check_complete(lst, requs):
    if len(lst) == len(requs) and len(requs) != 0:
        return True
    else:
        return False

@register.filter
def round_decimal(number):
    if type(number) != 'decimal.Decimal':
        try:
            number = decimal.Decimal(number)
        except TypeError:
            pass
    return round(number, 9)