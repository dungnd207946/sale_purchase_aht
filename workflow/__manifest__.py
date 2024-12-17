{
    'name': 'Workflow',
    'version': '1.0',
    'depends': ['base', 'web'],  # Phải thêm depends module gốc
    'data': [
        'security/ir.model.access.csv',
        'views/custom_workflow_views.xml',
        'views/state_in_model_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
             # Phải thêm đường dẫn của phần JS được import từ module gốc
            'workflow/static/src/**/*',
            # ('after', 'web/static/src/views/**/*', 'workflow/static/src/**/*')
        ],
    },
    'application': True,
    'installable': True,
}
