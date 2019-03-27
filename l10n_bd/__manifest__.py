# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

# Copyright (C) 2011 Smartmode LTD (<http://www.smartmode.co.uk>).

{
    'name': 'Bangladesh - Accounting',
    'version': '1.0',
    'category': 'Localization',
    'description': """
This is the latest Bangladesh Odoo localisation necessary to run Odoo accounting for Bangladesh SME's with:
=================================================================================================
   """,
    'author': 'SM Ashraf',
    'website': 'http://www.eagle_erp.com',
    'depends': [
        'account',
        'base_iban',
        'base_vat',
    ],
    'data': [
        'data/l10n_bd_chart_data.xml',
        'data/account.account.template.csv',
        'data/account.chart.template.csv',
        'data/account.account.tag.csv',
        'data/account.tax.group.csv',
        'data/account.tax.template.csv',
        'data/account_chart_template_data.yml',
    ],
    'demo' : ['demo/l10n_bd_demo.xml'],
}