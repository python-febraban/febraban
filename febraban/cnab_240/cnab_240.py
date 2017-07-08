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

import datetime
import logging
import re
import string
import unicodedata
from decimal import Decimal

from ..cnab import Cnab

_logger = logging.getLogger(__name__)
try:
    from cnab240.tipos import Arquivo
except ImportError as err:
    _logger.debug = err


class Cnab240(Cnab):
    """

    """

    def __init__(self):
        super(Cnab, self).__init__()

    @staticmethod
    def get_bank(bank):
        if bank == '341':
            from .bancos.itau import Itau240
            return Itau240
        elif bank == '237':
            from .bancos.bradesco import Bradesco240
            return Bradesco240
        elif bank == '104':
            from .bancos.cef import Cef240
            return Cef240
        elif bank == '033':
            from .bancos.santander import Santander240
            return Santander240
        else:
            return Cnab240

    def nosso_numero(self, format):
        return format

    def _prepare_header(
        self, arquivo_codigo, controle_banco,
        cedente_agencia, cedente_agencia_dv,
        cedente_conta, cedente_conta_dv, cedente_dv_ag_cc,
        cedente_inscricao_numero, cedente_inscricao_tipo,
        cedente_nome, nome_banco, servico_operacao, arquivo_sequencia,
        arquivo_data_de_geracao=False,
        arquivo_hora_de_geracao=False,
        **kwargs):
        """

        :param:
        :return:
        """
        return {
            'controle_banco': controle_banco,
            'arquivo_data_de_geracao':
                arquivo_data_de_geracao or self.data_hoje(),
            'arquivo_hora_de_geracao':
                arquivo_hora_de_geracao or self.hora_agora(),
            # TODO: Número sequencial de arquivo
            'arquivo_sequencia': int(arquivo_sequencia),
            'cedente_inscricao_tipo': int(self.inscricao_tipo(
                cedente_inscricao_numero
            )),
            'cedente_inscricao_numero':
                int(self.punctuation_rm(cedente_inscricao_numero)),
            'cedente_agencia': int(cedente_agencia),
            'cedente_conta': int(cedente_conta),
            'cedente_conta_dv': cedente_conta_dv,
            'cedente_agencia_dv': cedente_agencia_dv,
            'cedente_nome': cedente_nome,
            # DV ag e conta
            'cedente_dv_ag_cc': cedente_dv_ag_cc,
            'arquivo_codigo': 1,  # Remessa/Retorno
            'servico_operacao': unicode(servico_operacao),
            'nome_banco': unicode(nome_banco),
        }

    def _prepare_segmento(self, line):
        """
        :param line:
        :return:
        """
        prefixo, sulfixo = self.cep(line.sacado_cep)

        aceite = u'N'
        if not line.aceite == 'S':
            aceite = u'A'

        # Código agencia do cedente
        # cedente_agencia = cedente_agencia

        # Dígito verificador da agência do cedente
        # cedente_agencia_conta_dv = cedente_agencia_dv

        # Código da conta corrente do cedente
        # cedente_conta = cedente_conta

        # Dígito verificador da conta corrente do cedente
        # cedente_conta_dv = cedente_conta_dv

        # Dígito verificador de agencia e conta
        # Era cedente_agencia_conta_dv agora é cedente_dv_ag_cc

        return {
            # TODO: Esses dados podem ser de outras filiais e contas
            # provavelmente, então pode ser que teremos que refazer este
            # trecho.
            'controle_banco': self.arquivo.header.controle_banco,
            'cedente_agencia': self.arquivo.header.cedente_agencia,
            'cedente_conta': self.arquivo.header.cedente_conta,
            'cedente_conta_dv': self.arquivo.header.cedente_conta_dv,
            'cedente_agencia_dv': self.arquivo.header.cedente_agencia_dv,
            'cedente_dv_ag_cc': self.arquivo.header.cedente_dv_ag_cc,
            'identificacao_titulo': u'0000000',  # TODO
            'identificacao_titulo_banco': u'0000000',  # TODO
            'identificacao_titulo_empresa': line.nosso_numero,
            'numero_documento': line.numero_documento,
            'vencimento_titulo': self.format_date(
                line.data_vencimento
            ),
            'valor_titulo': Decimal(line.valor_documento).quantize(
                Decimal('1.00')),
            # TODO: Código adotado para identificar o título de cobrança.
            # 8 é Nota de cŕedito comercial
            'especie_titulo': 8,  # FIXME
                #int(self.order.mode.boleto_especie),
            'aceite_titulo': aceite,
            'data_emissao_titulo': self.format_date(
                line.data_documento),
            # TODO: trazer taxa de juros do Odoo. Depende do valor do 27.3P
            # CEF/FEBRABAN e Itaú não tem.
            'juros_mora_data': self.format_date(
                line.data_vencimento),  # FIXME
            'juros_mora_taxa_dia': Decimal('0.00'),  # FIXME
            'valor_abatimento': Decimal('0.00'),  # FIXME
            'sacado_inscricao_tipo': int(
                self.inscricao_tipo(line.sacado_documento)),
            'sacado_inscricao_numero': int(
                self.punctuation_rm(line.sacado_documento)),
            'sacado_nome': line.sacado_nome,
            'sacado_endereco': line.sacado_endereco,
            'sacado_bairro': line.sacado_bairro,
            'sacado_cep': int(prefixo),
            'sacado_cep_sufixo': int(sulfixo),
            'sacado_cidade': line.sacado_cidade,
            'sacado_uf': line.sacado_uf,
            'codigo_protesto': 1,
                #int(self.order.mode.boleto_protesto),
            'prazo_protesto':  1,
                #int(self.order.mode.boleto_protesto_prazo),
            'codigo_baixa': 2,
            'prazo_baixa': 0,  # De 5 a 120 dias.
            'controlecob_data_gravacao': self.data_hoje(),
            'cobranca_carteira': int(line.carteira),
        }

    def remessa(self, header, lista_boletos):
        """

        :param order:

        :return:
        """
        cobrancasimples_valor_titulos = Decimal(0.00)

        self.arquivo = Arquivo(self.bank, **self._prepare_header(**header))
        for line in lista_boletos:
            self.arquivo.incluir_cobranca(**self._prepare_segmento(line))
            self.arquivo.lotes[0].header.servico_servico = 1
            # TODO: tratar soma de tipos de cobranca
            # TODO: Verificar se é o valor do documento ou o valor
            cobrancasimples_valor_titulos += Decimal(line.valor_documento)
            self.arquivo.lotes[0].trailer.cobrancasimples_valor_titulos = \
                Decimal(cobrancasimples_valor_titulos).quantize(
                    Decimal('1.00'))

        remessa = unicode(self.arquivo)
        return unicodedata.normalize(
            'NFKD', remessa).encode('ascii', 'ignore')
