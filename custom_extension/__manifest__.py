{
    'name': 'Custom Sale Purchase',
    'version': '1.0',
    'author': "<DUNG>",
    'depends': ['sale', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/intermediate_report_views.xml',
        'views/stock_quant_period_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_extension/static/src/css/stock_quant_period_style.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}