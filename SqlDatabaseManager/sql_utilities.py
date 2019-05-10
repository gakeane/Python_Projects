
"""
Utilities for interacting with a local mysql database
Requires MySQLdb module to be installed

Once connection is established you must first choose which sql database you will work with using the select_database() method
If you wish to work on an other databse you must use the select_database() method again to change databases
Once a database is selected we can create/delete/query tables as well as add/delete/edit rows

The most useful method is the query function which lets you send SQL commands and returns the results
"""

import MySQLdb


# FIXME: Make private
def connect_to_database(host='localhost', user='root', password='Welcome1'):
    """ Returns a cursor object for interacting with the sql database """
    db = MySQLdb.connect(host=host, user=user, passwd=password)
    db.autocommit(True)
    return db.cursor()


# FIXME: Make private
def confirm_database_selected(func):
    """ warpper function for confirming a database has been selected """
    def wrapper(self, *args, **kwargs):
        self.db.execute("select database()")
        if self.db.fetchall()[0][0] == None:
            print "No database has been selected"
            return None
        else:
            return func(self, *args, **kwargs)
    return wrapper


# FIXME: Make private
def confirm_table_exists(func):
    """ Wrapper for confirming a table exists in the selected database """
    def wrapper(self, *args, **kwargs):
        if args[0] not in self.get_all_tables():
            print "Warning: Table [%s] does not exists" % args[0]
            return False
        else:
            return func(self, *args, **kwargs)
    return wrapper


class DatabaseUtils():
    def __init__(self, host='localhost', user='root', password='Welcome1'):
        """ Initiator for the database utils """
        self.db = connect_to_database(host, user, password)

    def get_all_databases(self):
        """ Returns a list with the names of all databases """
        self.db.execute("select schema_name as `Database` from information_schema.schemata")
        database_info = self.db.fetchall()
        return [data[0] for data in database_info]

    def select_database(self, db_name):
        """ selects a database for use """
        if db_name in self.get_all_databases():
            self.db.execute("use %s" % db_name)
        else:
            print "Warning: Database [%s] dose not exist" % db_name

    def create_database(self, db_name):
        """ Creates a database if it doesn't already exist """
        if db_name not in self.get_all_databases():
            self.db.execute("create database %s" % db_name)
        else:
            print "Warning: Database [%s] already exists" % db_name

    def delete_database(self, db_name):
        """ Delete a database if it exists """
        if db_name in self.get_all_databases():
            self.db.execute("drop database %s" % db_name)
        else:
            print "Warning: Database [%s] does not exists, deletion failure" % db_name

    @confirm_database_selected
    def get_all_tables(self):
        """ returns a list of all the tables in the selected database """
        self.db.execute("show tables")
        database_info = self.db.fetchall()
        return [data[0] for data in database_info]

    @confirm_database_selected
    def create_table(self, table_name, column_name, column_types):
        """
        Creates a tables with the specified columns in the selected database
        Table_name should be a string and column_name and column_tyoe should be a list of strings
        """
        if len(column_name) != len(column_types):
            print "Warning: List lenght of column names and column data types is not equal"
            return False # replace with raise
        if table_name in self.get_all_tables():
            print "Warning: Table [%s] already exists" % table_name
            return False
        cmd = 'create table %s (' + ','.join([s1 + ' ' + s2 for s1, s2 in zip(column_name, column_types)]) + ')'
        self.db.execute(cmd % table_name)
        return True

    @confirm_database_selected
    @confirm_table_exists
    def delete_table(self, table_name):
        """ Deletes a table from the selected database """
        self.db.execute('drop table %s' % table_name)
        return True

    @confirm_database_selected
    @confirm_table_exists
    def get_num_table_rows(self, table_name):
        """ Returns the number of rows in a table """
        self.db.execute('select count(*) from %s' % table_name)
        return self.db.fetchall()[0][0]

    @confirm_database_selected
    @confirm_table_exists
    def add_row_to_table(self, table_name, column_names, column_values):
        """ Adds a row to a table, data added is in the columns specified by column names """
        if len(column_names) != len(column_values):
            print "Warning: List lenght of column names and column values is not equal"
            return False # replace with raise
        cmd = 'insert into %s (' + ','.join(column_names) + ')' + ' values (' + ','.join(column_values) + ')'
        print cmd % table_name
        self.db.execute(cmd % table_name)

    @confirm_database_selected
    @confirm_table_exists
    def delete_row_from_table(self, table_name, column_name, column_value):
        """ Deletes a row from the selected table, deletes all rows with the specified column_value """
        print 'delete from %s where %s is %s' % (table_name, column_name, column_value)
        self.db.execute('delete from %s where %s = %s' % (table_name, column_name, column_value))

    def query(self, cmd):
        """ Runs a query command """
        self.db.execute(cmd)
        return self.db.fetchall()
