Changelog
=========

0.7.0 (2022-02-19)
------------------
- ISSUE-059: Added bump2version. (fe379f2) [Roderick Constance]
- ISSUE-056: Fixed logger_noformat, enabled pre-commit, pytest. (0336b12) [Roderick Constance]
- ISSUE-056: Added csv_str parsing, api loglevel setting. (4ddf085) [Roderick Constance]

0.6.6 (2021-04-26)
------------------
- ISSUE-053: Disabled sort_dicts param until python-3.8. (55775b1) [JustAddRobots]

0.6.5 (2021-04-21)
------------------
- ISSUE-050: Changed module version/title output loglevel to DEBUG. (345f224) [JustAddRobots]

0.6.4 (2021-04-21)
------------------
- Stage: Updated for MacOS getopt. (137b6c3) [JustAddRobots]
- Stage: Fixed hashbang for bash env. (eeeb720) [JustAddRobots]
- ISSUE-047: Added sort_dicts to get_debug() (95b8a9c) [JustAddRobots]

0.6.3 (2020-12-20)
------------------
- ISSUE-042: Removed whitespace. (b97f9ab) [JustAddRobots]
- ISSUE-042: Added installation notes. (677caf7) [JustAddRobots]

0.6.2 (2020-12-14)
------------------
- ISSUE-033: Fixed typo. (8435e0c) [JustAddRobots]

0.6.1 (2020-12-14)
------------------
- ISSUE-033: Fixed env var definitions. (0169f5e) [JustAddRobots]

0.6.0 (2020-12-14)
------------------
- Stage: Fixed delete tags stage indentation. (149e6a2) [JustAddRobots]
- ISSUE-033: Added delete RC tags to pipeline, misc docs. (0ceb258) [JustAddRobots]

0.5.2 (2020-12-11)
------------------
- ISSUE-014: Updated to use INI_URL constant. (9bbc99e) [JustAddRobots]

0.5.1 (2020-12-10)
------------------
- Stage: Cleaned up Jenkinsfile. (d9e8b6a) [JustAddRobots]
- Stage: Updated Jenkinsfile for JSON INI URL. (3edb1b3) [JustAddRobots]
- ISSUE-014: Changed INI format to JSON. (84b1802) [JustAddRobots]

0.5.0 (2020-12-09)
------------------
- Stage: Added both DOCKERHOST and SERVER for runxhpl INI integration. (4007d62) [JustAddRobots]
- Stage: Fixed dockerhost/buildhost transposition. (69ac161) [JustAddRobots]
- Stage: Troubleshooting Jenkins workspace/loadProperties() (6b1121f) [JustAddRobots]
- Stage: Added loadProperties() to first build stage. (940ca33) [JustAddRobots]
- Stage: Troubleshooting INI file location in Jenkins workspace. (660fb5d) [JustAddRobots]
- ISSUE-014: Removed "" from INI file. (f33d8f3) [JustAddRobots]
- ISSUE-014: Added INI config file. (81a4b58) [JustAddRobots]

0.4.0 (2020-12-08)
------------------
- ISSUE-022: Added misc fixes. (0df9859) [JustAddRobots]
- ISSUE-023: Fixed typo in README. (54a0117) [JustAddRobots]
- ISSUE-023: Added LICENSE, update README. (d7b318a) [JustAddRobots]

0.3.0 (2020-12-06)
------------------
- Stage: Switched to Jenkins GIT_COMMIT env var. (2bb2920) [JustAddRobots]
- Stage: Added HASHSHORT_FIELD. (9d078a0) [JustAddRobots]
- Stage: Added HASHSHORT as env var. (0d3b824) [JustAddRobots]
- Stage: Changed ENGCOMMON_BRANCH SELECTOR from branch to hash. (ea6d0ea) [JustAddRobots]
- Stage: Added ENGCOMMON_BRANCH selector. (df6c8e1) [JustAddRobots]
- ISSUE-019: Added more unit tests. (3a24db3) [JustAddRobots]
- ISSUE-019: Removed unnecessary __init__.py from unit tests. (82c95d8) [JustAddRobots]
- ISSUE-019: Added unit tests, pytest to pre-commit. (1abb5bd) [JustAddRobots]

0.2.0 (2020-11-23)
------------------
- ISSUE-016: Added hardware functions for uuid and serial_num. (df72f20) [JustAddRobots]

0.1.4 (2020-11-20)
------------------
- Stage: Removed extra whitespace from slackSend. (0754788) [JustAddRobots]
- Stage: Cleaned up Jenkinsfile after first successful build. (35323b2) [JustAddRobots]
- Stage: Added failFast for parallel builds. (4550189) [JustAddRobots]
- Stage: Fixed slackSend post. (87f3b31) [JustAddRobots]
- Stage: Fixed continuation char, added post success/failure. (9377ff2) [JustAddRobots]
- Stage: Fixed syntax. (e271f02) [JustAddRobots]
- Stage: Fixed typo. (02bcd4a) [JustAddRobots]
- Stage: Removed 'steps' directive. (6d2c4f6) [JustAddRobots]
- Stage: Fixed syntax. (67e398d) [JustAddRobots]
- Stage: Fixed syntax. (39c2ac6) [JustAddRobots]
- Stage: Fixed syntax. (32f3f91) [JustAddRobots]
- Stage: Changed 'master' to 'main' (586c73a) [JustAddRobots]
- Stage: Fixed typo. (a439dbb) [JustAddRobots]
- Stage: Fixed GitSCM plugin credentialsID sytax. (7c77c6d) [JustAddRobots]
- Stage: Fixed syntax. (4c4e694) [JustAddRobots]
- Stage: Fixed syntax. (694ecff) [JustAddRobots]
- Stage: Fixed syntax. (33947ec) [JustAddRobots]
- Stage: Fixed syntax. (973d610) [JustAddRobots]
- Stage: Fixed parallel syntax. (a675377) [JustAddRobots]
- Stage: Fixed parallel build syntax. (a1e8522) [JustAddRobots]
- Stage: Fixed syntax error. (81e9a1a) [JustAddRobots]
- Stage: Fixed syntax errors. (920a4c7) [JustAddRobots]
- Stage: (2e2a368) [JustAddRobots]
- Stage: Updated Jenkinsfile for parallel pipelines. (286cce0) [JustAddRobots]
- Stage: Fixed syntax errors. (2b88d08) [JustAddRobots]
- Stage: Fixed syntax error. (60eb871) [JustAddRobots]
- Stage: Fixed syntax errors. (53ad836) [JustAddRobots]
- LOAD-012: Updated Jenkins creds for new instance. (51fbdc7) [JustAddRobots]

0.1.2 (2020-11-16)
------------------
- ISSUE-007: Fixed flag/extension vocabulary. (12610ec) [JustAddRobots]
- ISSUE-004: Added DMIdecode. (645cc3c) [JustAddRobots]
- ISSUE-003: Activated pre-commit, added fixes. (5f75eea) [JustAddRobots]
- ISSUE-001: Added miscellaeous bits after util module removal. (907235e) [JustAddRobots]
- ISSUE-001: Removed util module references. (9971514) [JustAddRobots]
- ISSUE-001: Added more bits, broke apart util module. (4abddb7) [JustAddRobots]
- ISSUE-001: Adding more bits for rebuild / rewrite. (0a7889a) [JustAddRobots]
- ISSUE-001: Added bits to start normalising POC. (7ee0359) [JustAddRobots]
- Initial commit. (c2c9c93) [JustAddRobots]
