{
    "name": "Left Sidebar Menu",
    "summary": "Move the Odoo app and section menus to a scrollable left sidebar.",
    "version": "19.0.1.0.0",
    "author": "Duskwrath, Saw Lwin Oo",
    "depends": ["web"],
    "assets": {
        "web.assets_backend": [
            "slo_web_left_sidebar_menu/static/src/**/*",
        ],
    },
    "license": "LGPL-3",
    "installable": True,
    "application": True,
}
