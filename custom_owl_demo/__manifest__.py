{
    'name': 'Custom Owl Demo',
    'version': '1.0',
    'depends': ['base', 'web'],
    'data': [
        'views/owl_menu.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'custom_owl_demo/static/src/js/main.js',
            'custom_owl_demo/static/src/js/owl_component.js',
            'custom_owl_demo/static/src/css/style.css',
        ],
        'web.assets_qweb': [
            'custom_owl_module/static/src/xml/owl_templates.xml',
        ],
    },
    'application': True,
    'installable': True,
}
