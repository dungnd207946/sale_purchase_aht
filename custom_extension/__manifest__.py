{
    'name': 'Custom Sale Purchase',
    'version': '1.0',
    'author': "<DUNG>",
    'depends': ['sale', 'purchase', 'stock'],
    'data': [
        'security/ir.model.access.csv',
        'views/intermediate_report_views.xml',
    ],
    'assets': {
        'web.assets_backend': [],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}