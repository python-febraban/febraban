# coding: utf-8
# ###########################################################################
#
#    Author: Luis Felipe Mileo
#            Fernando Marcato Rodrigues
#            Daniel Sadamo Hirayama
#    Copyright 2015 KMEE - www.kmee.com.br
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################

import time
import re
import string


class Cnab(object):

    def __init__(self):
        pass

    @staticmethod
    def get_cnab(banco, layout='240'):
        if layout == '240':
            from .cnab_240.cnab_240 import Cnab240
            return Cnab240.get_bank(banco)
        elif layout == '400':
            from .cnab_400.cnab_400 import Cnab400
            return Cnab400.get_bank(banco)
        elif layout == '500':
            from .pag_for.pag_for500 import PagFor500
            return PagFor500.get_bank(banco)
        else:
            return False

    def remessa(self, header, lista_boletos):
        return False

    def retorno(self, cnab_file):
        return object

    def data_hoje(self):
        return (int(time.strftime("%d%m%Y")))

    def hora_agora(self):
        return (int(time.strftime("%H%M%S")))

    def cep(self, format):
        sulfixo = format[-3:]
        prefixo = format[:5]
        return prefixo, sulfixo

    @staticmethod
    def punctuation_rm(string_value):
        tmp_value = (
            re.sub('[%s]' % re.escape(string.punctuation),
                   '', string_value or ''))
        return tmp_value

    def inscricao_tipo(self, sacado_documento):
        # TODO: Implementar codigo para PIS/PASEP
        if len(self.punctuation_rm(sacado_documento)) > 11:
            return 1
        else:
            return 2

    def format_date(self, srt_date):
        return int(srt_date.strftime('%d%m%Y'))
