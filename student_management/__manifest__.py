{
    'name': 'Student Management',
    'version': '1.0',
    'author': "<DUNG>",
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/grade_views.xml',
        'views/student_views.xml',
        'views/school_views.xml',
        'views/class_views.xml',
        'wizard/student_search_views.xml',
        'views/menu_item_views.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'student_management/static/src/css/student_style.css',
        ],
    },
    'application': True,
    'installable': True,
    'auto_install': False,
}