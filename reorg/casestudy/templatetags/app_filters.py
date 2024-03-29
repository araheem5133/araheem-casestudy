from django import template

register = template.Library()

#Used for gaining name attribute in home.html
@register.filter(name='attr') 
def attr(obj, attribute):
    return getattr(obj, attribute)