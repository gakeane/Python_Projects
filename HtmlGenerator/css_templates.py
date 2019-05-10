
"""
This module contains templates of CSS
These can be applied to the style filed of HTML reports
"""


TABLE_CSS = """
            table {
                font-family: "Trebuchet MS", Arial, Helvetica, sans-serif;
                border-collapse: collapse;
                width: 100%;
            }

            td, th {
                border: 1px solid #ddd;
                padding: 8px;
            }

            tr:nth-child(even) {
                background-color: #f2f2f2;
            }

            tr:hover {
                background-color: #ddd;
            }

            th {
                padding-top: 12px;
                padding-bottom: 12px;
                text-align: left;
                background-color: #4CAF50;
                color: white;
            }

            .main_title_wrapper {
                padding-top: 30px;
                text-align: center;
            }

            .sub_title_wrapper {
                text-align: center;
            }
"""
