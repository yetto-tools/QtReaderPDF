from __future__ import print_function, unicode_literals

from num2words.lang_ES import Num2Word_ES
from num2words import CONVERTER_CLASSES



class TypeCents:
    GENERIC_CENTS = ('Centavo', 'Centavos')
    NUMERIC_CENTS = ('/100','/100')


Num2Word_ES.CURRENCY_ADJECTIVES.update({'GTQ': 'Guatemala'})
Num2Word_ES.CURRENCY_FORMS.update({'GTQ': (('Quetzal', 'Quetzales'), TypeCents.GENERIC_CENTS)})


class Num2Word_ES_GT(Num2Word_ES):

    def set_cents(self, TYPE_CENTS):
        Num2Word_ES.CURRENCY_FORMS.update({'GTQ': (('Quetzal', 'Quetzales'), TYPE_CENTS)})

    def to_currency(self, val, currency='GTQ', cents=True, separator=' con', adjective=False):
        if cents == False:
            self.set_cents(TypeCents.NUMERIC_CENTS)
            result = super(Num2Word_ES, self).to_currency(
                val, currency=currency, cents=cents, separator=separator,
                adjective=adjective)
        elif cents == True:
            self.set_cents(TypeCents.GENERIC_CENTS)
            result = super(Num2Word_ES, self).to_currency(
                val, currency=currency, cents=cents, separator=separator,
                adjective=adjective)
        # Handle exception, in spanish is "un Quetzal" and not "uno Quetzal"
        return result.replace("uno", "un")

CONVERTER_CLASSES.update({'gt' : Num2Word_ES_GT()})


