
"""
Module contains utilities for creating modifying html content

The approach used in this module is to take a string and wrap it in html tags as required
The html tags can be assigned classes so that they can be identified by CSS
"""

import json
import os

from pprint import pprint as pp

from utils.testlink_utils.testlink_constants import CURR_PROJECT_VER
from utils.html_utils.html_templates import HTML_PAGE, TABLE_TEMPLATE


def _html_element_wrapper(element_type, html_str, classes=None):
    """ Wraps string in a html element

    element_type: (str) Indicates the type of element tags
    html_str: (str) html code to be wrapped in a div tag
    classes: (str) string of space seperated css class  names
    """

    if not isinstance(html_str, str):
        raise ValueError("First arg must have type string but has type %s" % type(html_str))

    if classes and not isinstance(classes, str):
        raise ValueError("second arg must have type string but has type %s" % type(classes))

    if classes:
        return "<%s class=\"%s\">\n%s</%s>\n\n" % (element_type, classes, html_str, element_type)

    return "<%s>\n%s\n</%s>\n\n" % (element_type, html_str, element_type)


def div(html_str, classes=None):
    """ Wraps string in html div element """

    return _html_element_wrapper("div", html_str, classes)


def table(html_str, classes=None):
    """ Wraps html string in table tags """

    return _html_element_wrapper("table", html_str, classes)


def make_table_row(table_row_data, table_row_classes=None, table_element_classes=None, table_header=False):
    """ creates a html table row given the data to be placed in the row

    table_row_data: (list(str)) list of strings containing the information for each cell
    table_row_classes: (str) string of space seperated css class names
    table_element_classes: (dict) key: table_row_data equivilent, value: string of space seperated css class names
    table_header: (boolean) If true will create a table header row
    """

    cell_type = "th" if table_header else "td"
    html = "<tr class=\"%s\">\n" % table_row_classes if table_row_classes else "<tr>\n"

    for element in table_row_data:
        if table_element_classes and table_row_data in table_element_classes.keys():
            html += "\t<%s class=\"%s\">%s</%s>\n" % (cell_type, table_element_classes[element], element, cell_type)
        else:
            html += "\t<%s>%s</%s>\n" % (cell_type, element, cell_type)

    html += "</tr>\n"
    return html


def create_html_table_from_data(table_headings, table_data, table_name):
    """ Takes in a list of tuples as data for the table, returns the data as an html table """
    table_head = '<tr>' + '<th>%s</th>' * len(table_headings) + '</tr>\n'
    table_body = ''
    for item in table_data:
        table_line = '<tr>' + '<td>%s</td>' * len(item) + '</tr>\n'
        table_body += table_line % tuple(item)

    table_content = table_head % tuple(table_headings) + table_body
    table_content = TABLE_TEMPLATE.replace('TABLE_CONTENT', table_content)
    table_content = table_content.replace('TABLE_NAME', table_name)
    return table_content


def create_html_report_from_data(content):
    pass


def add_content_to_page(content, page_name, css=None):
    """ Adds content to an html page and returns the html code """
    page_title = 'PCA %s Testlink Report - %s' % (CURR_PROJECT_VER, page_name)
    report = HTML_PAGE.replace('PAGE_TITLE', page_title)
    report = report.replace('PAGE_CONTENT', content)

    if css:
        report = report.replace('CSS_CONTENT', css)
    else:
        report = report.replace('CSS_CONTENT', '')

    return report



def write_html_to_file(html, file_path='index.html'):
    """ Writes html string to a file """

    # FIXME make sure path exists
    with open(file_path, 'w') as f:
        f.write(str(html))
