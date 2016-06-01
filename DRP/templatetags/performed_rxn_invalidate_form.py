
from django import template
from DRP.forms import PerformedRxnInvalidateForm

register = template.Library()

def rxnInvalidateFormId():
  if not hasattr(rxnInvalidateFormId, 'count'):
    rxnInvalidateFormId.count = 0
  else:
    rxnInvalidateFormId.count +=1
  return rxnInvalidateFormId.count

@register.simple_tag(takes_context=True)
def performed_rxn_invalidate_form(context, instance):
  return PerformedRxnInvalidateForm(instance=instance, user=context['user'], auto_id='%s_{}'.format(rxnInvalidateFormId())).as_ul()
