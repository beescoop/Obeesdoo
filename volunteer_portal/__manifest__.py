{ 
    "name": "Volunteer Portal",
    "summary": """
        Volunteers portal""",
    "version": "16.0.0.8.0",
    "category": "Volunteer shifts management portal",
    "website": "https://github.com/beescoop/Obeesdoo",
    "author": "Coop IT Easy SC",
    "maintainers": ["anaRtem1s", "remytms"],
    "license": "AGPL-3",
    #?anartemis test
    "application": False,
    #?anartemis: added "portal" and other related modules
    "depends": ["mail", "portal", "volunteer", "volunteer_attendance"],
    "data": [
        "views/portal_templates.xml",
    ],
    "assets": {
        "web.assets_frontend": [
            "volunteer_portal/static/src/scss/volunteer_portal.scss",
        ],
    },
}
