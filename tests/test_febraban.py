#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Tests for `febraban` package."""

import pytest

from click.testing import CliRunner

from febraban.boleto import Boleto
from febraban.cnab import Cnab
from febraban import cli

from datetime import datetime, timedelta


@pytest.mark.webtest
class TestRemessaBradesco240(object):

    def test_remessa_boleto_bradesco_240(self):
        """+Scenario 1: Emissão de boleto registrado bradesco+
            Dado uma lista de boletos bradesco
            Quando o usuário emite uma remessa no layout 240
            Então um arquivo de remessa é retornado"""

        lista_boletos = []

        bank_bic = u'237'

        boleto = Boleto.get_class_for_codigo(bank_bic)

        boleto.cedente = u'KMEE INFORMATICA LTDA'
        boleto.cedente_documento = u'23.130.935/0001-98'
        boleto.cedente_bairro = u'Pinheirinho'
        boleto.cedente_cep = u'37500-050'
        boleto.cedente_cidade = u'Itajubá'
        boleto.cedente_logradouro = u'Rua Coronel Renno' + u', ' + u'1275'
        boleto.cedente_uf = u'MG'

        cedente_conta = u'308'
        cedente_conta_dv = u'0'
        cedente_agencia = u'12345'
        cedente_agencia_dv = u'7'

        boleto.agencia_cedente = cedente_conta + '-' + cedente_conta_dv
        boleto.conta_cedente = cedente_agencia + '-' + cedente_agencia_dv

        boleto.sacado_endereco = u'Rua dos ferroviários' + u', ' + u'1000'
        boleto.sacado_cidade = u'Jacareí'
        boleto.sacado_bairro = u'Centro'
        boleto.sacado_uf = u'SP'
        boleto.sacado_cep = u'12315-030'
        boleto.sacado_nome = u'Sacado Genérico'
        boleto.sacado_documento = u'53939351000129'

        boleto.convenio = '06'
        boleto.especie_documento = u'DM'
        boleto.aceite = u'S'  # Ou 'N'
        boleto.carteira = '06'

        boleto.data_vencimento = datetime.now()+timedelta(10)
        boleto.data_documento = datetime.now()
        boleto.data_processamento = datetime.now()
        boleto.valor = str("%.2f" % 15000.00)
        boleto.valor_documento = str("%.2f" % 15000.00)
        boleto.especie = u'R$'
        boleto.quantidade = ''  # str("%.2f" % move_line.amount_currency)
        boleto.numero_documento = u'1000/1'
        boleto.nosso_numero = u'2125525'

        lista_boletos.append(boleto)

        cnab = Cnab.get_cnab(banco='237', layout='240')()

        header = {
            'arquivo_sequencia': 1,
            'controle_banco': bank_bic,
            'cedente_inscricao_tipo': 2,
            'cedente_inscricao_numero': boleto.cedente_documento,
            'cedente_conta': cedente_conta,
            'cedente_conta_dv': cedente_conta_dv,
            'cedente_agencia': cedente_agencia,
            'cedente_agencia_dv': cedente_agencia_dv,
            'cedente_nome': boleto.cedente,
            # DV ag e conta
            'cedente_dv_ag_cc': boleto.agencia_cedente[-1],  # ????
            'arquivo_codigo': 1,  # Remessa/Retorno
            'servico_operacao': u'R',
            'nome_banco': u'Banco Bradesco S/A',
        }

        arquivo = cnab.remessa(header, lista_boletos)
        print arquivo


def test_command_line_interface():
    """Test the CLI."""
    runner = CliRunner()
    result = runner.invoke(cli.main)
    assert result.exit_code == 0
    assert 'febraban.cli.main' in result.output
    help_result = runner.invoke(cli.main, ['--help'])
    assert help_result.exit_code == 0
    assert '--help  Show this message and exit.' in help_result.output
