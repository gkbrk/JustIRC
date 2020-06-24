project = "JustIRC"
author = "Gokberk Yaltirakli"
copyright = "2020, Gokberk Yaltirakli"

extensions = ['sphinx.ext.autodoc', 'sphinx.ext.napoleon']

html_theme = "alabaster"

html_sidebars = {
    '**': [
        'about.html',
        'localtoc.html',
        'donate.html',
    ]
}

html_theme_options = {
    'github_user': 'gkbrk',
    'github_repo': 'JustIRC',
    'github_type': 'star',
    'donate_url': 'https://www.gkbrk.com/donate'
}
