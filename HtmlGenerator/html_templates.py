
"""
This module contains templates of CSS
These can be used to quickly create html elements and pages

# FIXME: import project version from testlink_constants
# FIXME: import getdate from general_utilities
"""

from datetime import datetime

# Generic html page
HTML_PAGE = """
<html>
    <head>
        <title>PAGE_TITLE</title>

        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">

        <style>
            CSS_CONTENT
        </style>
    </head>

    <body>
        <p>Report Generated: %s</p>
        PAGE_CONTENT
    </body>
</html>""" % datetime.now().strftime('%Y-%m-%d %H:%M:%S')

# Generic table template
TABLE_TEMPLATE = """
<table border="1">
    <caption>PCA 2.4.1 TestLink Report - TABLE_NAME</caption>
    TABLE_CONTENT
</table>
"""
