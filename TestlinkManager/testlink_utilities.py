
"""
This module provides a class for connecting to the testlink server REST API
This class relies on the TestLinkHelper module and TestlinkAPIClient module which must be installed on the running machine

The class includes get methods for retriving information from the testlink webserver
This class also inculdes methods for altering information on the testlink webserver
"""

import re

from pprint import pprint as pp
from datetime import datetime

from testlink.testlinkapi import TestlinkAPIClient
from testlink.testlinkhelper import TestLinkHelper
from utils.testlink_utils.testlink_constants import *


def get_upgrade_paths():
    """ Finds all the possible upgrade paths to the current test version and filters this list based on MAX_NUM_UPGRADES """
    paths = [CURR_PROJECT_VER]

    for ver in reversed(SUPPORTED_VERSIONS[:-1]):
        temp_paths = []
        for path in paths:
            temp_paths.append('%s->%s' % (ver, path))
        paths.extend(temp_paths)

    # apply filtering conditions to list of upgrade paths
    paths[0] = FRESH + ' OPUS'
    paths.insert(0, FRESH + ' CISCO')
    paths = [path for path in paths if path.count('->') <= MAX_NUM_UPGRADES]
    paths.extend([path + MIXED for path in paths[2:]])
    paths.append(CURR_PROJECT_VER + '->' + CURR_PROJECT_VER)
    return paths


def get_upgrade_path_from_build(build):
    """ Given a valid build name this will extract the upgrade path from it """
    # FIXME improve the regular expression to detect more poorly entered upgrade paths

    build = build.lower()
    if MANDATORY_BUILD_PREFIX not in build:
        print 'Invalid Build Prefix [%s]' % build
        return 'Unknown Path'
    build = build.replace(MANDATORY_BUILD_PREFIX, '')
    regex = '(\s*(->)?\s*(\d\.\d\.\d)){1,5}'
    match = re.search(regex, build)
    if match:
        path = match.group().replace(' ', '')
        if path == CURR_PROJECT_VER:
            return FRESH + ' CISCO' if any(rack_name in build for rack_name in CISCO_RACKS) else FRESH + ' OPUS'
        else:
            return path + MIXED if 'mixed' in build else path
    print 'Unrecognized upgrade path [%s]' % build
    return 'Unknown Path'


def get_info_from_build_name(build):
    """ Function which will extract the build, upgrade path, rack and architecture from a build """
    build_match = re.search('%s-b\d*' % CURR_PROJECT_VER, build)
    build_name = build_match.group() if build_match else 'N/a'

    rack_match = re.search('((burl|dub)[\d\-\_]+)_X', build)
    rack = rack_match.group(1) if rack_match else 'N/a'

    arch_match = re.search('[Xx]\d[-_]2', build)
    arch = arch_match.group() if arch_match else 'N/a'

    path = get_upgrade_path_from_build(build)
    return path, build_name, rack, arch


# FIXME: Probably don't need this
def connect_to_testlink(testlink_server_url, developer_key):
    """ Establishes a connection to a testlink server for a specific developer """
    tl_client = TestlinkAPIClient
    tl_helper = TestLinkHelper(testlink_server_url, developer_key)
    tl_helper._proxy = None

    return tl_helper.connect(tl_client)


# FIXME: Can be moved to general utilities
def list_to_dict(l, key):
    """ Converts a list of dictionaries to a dictionary of dictionaries based on a specified key """
    return_dict = {}
    for d in l:
        try:
            return_dict[d[key]] = d
        except KeyError:
            print "WARNING: Key [%s] is not valid, must be one of %s, Skipping entry" % (key, d.keys())
    return return_dict


class TestLinkSession():

    def __init__(self, testlink_server_url=TESTLINK_SERVER_URL, developer_key=TEST_RUNNER_DEV_KEY, project_id=CURR_PROJECT_ID):
        """ Creates an object for handling communication with a test link project """
        self._tl_connection = connect_to_testlink(testlink_server_url, developer_key)
        self._project_number = project_id

    def get_projects(self):
        """ Returns a list of dictionaries containing information about all projects in testlink """
        return self._tl_connection.getProjects()

    def get_project_id(self, project_name):
        """ Returns the ID for a project given the project name (i.e. OVCA2.3.3), None if name not found """
        for project in self.get_projects():
            if project['name'] == project_name:
                return project['id']
        return None

    def get_test_plans(self):
        """ Returns a list of dictionaries containing information for each testplan in project (only returns active plans) """
        plans = self._tl_connection.getProjectTestPlans(self._project_number)
        return [plan for plan in plans if plan['active'] ==  '1']

    def get_test_plan_ids(self):
        """ Returns a list if the internal id for each test plan in the project """
        return [plan['id'] for plan in self._tl_connection.getProjectTestPlans(self._project_number)]

    def get_test_case_info_from_plan(self, plan_id):
        """ Given the testplan id returns a list of dictionaries containing information on each testcase in the plan """
        return [testcase.values()[0] for testcase in self._tl_connection.getTestCasesForTestPlan(plan_id).values()]

    def get_test_case_ids_from_plan(self, plan_id):
        """ Given the testplan id returns a list of the internal ids for each testcase in the plan """
        return [testcase.values()[0]['tcase_id'] for testcase in self._tl_connection.getTestCasesForTestPlan(plan_id).values()]

    def get_test_case_info_from_build(self, plan_id, build_id):
        """ Returns a list of dictionaries containing information on all test for a certain build in a testplan """
        return [testcase.values()[0] for testcase in self._tl_connection.getTestCasesForTestPlan(plan_id, buildid=build_id).values()]

    def get_test_case_details(self, tc_id):
        """ Returns details about a specific testcase """
        return self._tl_connection.getTestCase(tc_id)[0]

    def get_build_info_from_plan(self, plan_id):
        """ Returns a list of dictionaries containing information about each build in the test plan """
        return self._tl_connection.getBuildsForTestPlan(plan_id)

    def get_build_ids_from_plan(self, plan_id):
        """ Returns a list of the internal ids for each build in the test plan """
        return [build['id'] for build in self._tl_connection.getBuildsForTestPlan(plan_id)]

    def get_build_info_from_plan_as_dict(self, plan_id, key='id'):
        """ Returns the build information of a testplan as a dictionary of dictionaries """
        return list_to_dict(self.get_build_info_from_plan(plan_id), key)

    def get_test_plan_platforms(self, plan_id):
        """ Returns a list of dictionaries with information about all the platforms on a testplan """
        return self._tl_connection.getTestPlanPlatforms(plan_id)

    def get_test_case_info_from_platform(self, plan_id, platform_id):
        """ Returns a list of dictionaries containing information on all test for a certain platform in a testplan """
        return [testcase.values()[0] for testcase in self._tl_connection.getTestCasesForTestPlan(plan_id, platformid=platform_id).values()]

    def get_execution_info(self, plan_id, tc_id):
        """ Returns execution information for all executions of a test """
        return self._tl_connection.getLastExecutionResult(plan_id, tc_id)[0]

    def get_last_execution_info(self, plan_id, tc_id):
        """ Returns information about the last time a test case was executed in a given plan """
        result = self._tl_connection.getLastExecutionResult(plan_id, tc_id)[0]
        return result if isinstance(result, dict) else result[0]

    def set_test_case_execution_type(self, tc_ext_id, type=1):
        """ Sets the execution type for a test in testlink to either manual or automated

        tc_ext_id: (string) The external ID of the test to be modified
        type:      (int)    set to 1 for manual, set to 2 for automated
        """
        self._tl_connection.setTestCaseExecutionType(testprojectid=CURR_PROJECT_ID, version=1, executiontype=type,
                                                     testcaseexternalid=EXTERNAL_ID_PREFIX % tc_ext_id)

    def get_test_case_info_from_id(self, tc_id):
        """ Given the test case id returns a large amount of information about a testcase in a dictionary """
        testcase = self._tl_connection.getTestCase(tc_id)[0]
        if testcase['importance'] == '1':
            testcase['importance'] = 'LOW'
        elif testcase['importance'] == '2':
            testcase['importance'] = 'MEDIUM'
        else:
            testcase['importance'] = 'HIGH'

        return testcase['testcase_id'], {'id': testcase['tc_external_id'],
                                         'name': testcase['name'].replace(u'\u2013', '-'),
                                         'importance': testcase['importance'],
                                         'creation_ts': testcase['creation_ts'],
                                         'x0-2_exec': 0,
                                         'x0-2_pass': 0,
                                         'x0-2_fail': 0}

    def get_filtered_test_case_info_from_plan(self, plan_id):
        """
        Returns a dictionary of dictionaries containg information about every test case in a testplan
        The key to the top level dictionary is the tests internal id
        """
        testcases = self.get_test_case_ids_from_plan(plan_id)
        filtered_info = {}
        for testcase in testcases:
            tc_id, tc_info = self.get_test_case_info_from_id(testcase)
            filtered_info[tc_id] = tc_info
        return filtered_info

    def determine_test_case_execution(self, test_case_info, plan_id):
        """ For a given test plan determines how many times each test has passed or failed accross all builds """
        build_ids = self.get_build_ids_from_plan(plan_id)
        for build_id in build_ids:
            for testcase in self._tl_connection.getTestCasesForTestPlan(plan_id, buildid=build_id).values():
                testcase_execution = testcase.values()[0]['exec_status']
                testcase_id = testcase.values()[0]['tcase_id']
                if testcase_execution == 'p':
                    test_case_info[testcase_id]['x0-2_exec'] += 1
                    test_case_info[testcase_id]['x0-2_pass'] += 1
                elif testcase_execution == 'f':
                    test_case_info[testcase_id]['x0-2_exec'] += 1
                    test_case_info[testcase_id]['x0-2_fail'] += 1

    def determine_test_case_execution_per_path(self, plan, tested_paths):
        """ Fills a dictionary with the execution status for each test on each possible build path """
        identified_tests = {}
        for path in tested_paths:
            print path['name']
            path_name = get_upgrade_path_from_build(path['name'])
            identified_tests.setdefault(path_name, {})
            run_tests = identified_tests[path_name].keys()
            test_cases = self.get_test_case_info_from_build(plan['id'], path['id'])

            for test_case in test_cases:
                if test_case['tc_id'] not in run_tests:
                    # add test execution and importance as a tuple to dictionary
                    identified_tests[path_name][test_case['tc_id']] = {'e':test_case['exec_status'], 'p':0, 'f':0, 'b':0}
                    if test_case['exec_status'] != 'n':
                        identified_tests[path_name][test_case['tc_id']][test_case['exec_status']] += 1
                else:
                    # update dictionary with most recent build
                    if test_case['exec_status'] != 'n':
                        identified_tests[path_name][test_case['tc_id']]['e'] = test_case['exec_status']
                        identified_tests[path_name][test_case['tc_id']][test_case['exec_status']] += 1
        return identified_tests

    def find_not_run_for_n_days(self, plan_id, num_days=-1):
        """
        Returns a dictionary of tests not run for num_days days for a test plan based on test priority
        Setting num_days to -1 effectly sets num_days to infinity (ie only checks if a test was run)
        """
        curr_time = datetime.now()
        not_run_tests = {'HIGH':[], 'MEDIUM':[], 'LOW':[]}
        testcases = self.get_filtered_test_case_info_from_plan(plan_id)
        for tc_id, tc_data in testcases.items():
            exec_result = self.get_last_execution_info(plan_id, tc_id)
            if exec_result['id'] != -1:
                last_execution_date = datetime.strptime(exec_result['execution_ts'],'%Y-%m-%d %H:%M:%S')
                if num_days == -1 or (curr_time - last_execution_date).days <= num_days:
                    continue
            not_run_tests[tc_data['importance']].append((tc_data['id'], tc_data['name']))
        return not_run_tests

    def print_all_testcases(self):
        for test_suite in self._tl_connection.getFirstLevelTestSuitesForTestProject(self._project_number):
            print '=%s=' % test_suite['name']
            for test_case in self._tl_connection.getTestCasesForTestSuite(test_suite['id'], True, 'full'):
                print '\t=>Test Case ID: %s, Test Case Name: %s' % (test_case['tc_external_id'],
                                                                    test_case['name'].replace(u'\u2013', '-'))
