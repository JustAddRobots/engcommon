#!/usr/bin/env groovy

def HASHLONG
def HASHSHORT
def TAG
def TAG_HASH
def BRANCH

pipeline {
    agent any
    environment {
        ARCH = sh(returnStdout: true, script: 'uname -m').trim()
        KUBECONFIG = '/usr/local/etc/kube_config'
    }
    stages {
        stage ('Create Git Tag Hash') {
            steps {
                script {
                    HASHLONG = sh(
                        returnStdout: true,
                        script: 'git log -1 --pretty=%H --no-merges'
                    ).trim()
                    HASHSHORT = sh(
                        returnStdout: true,
                        script: 'git log -1 --pretty=%h --no-merges'
                    ).trim()
                    TAG = sh(
                        returnStdout: true,
                        script: 'git describe --tags --abbrev=0'
                    ).trim()
                    TAG_HASH = "${TAG}-${HASHSHORT}-${ARCH}"
                }
                echo "ARCH: ${env.ARCH}"
                echo "COMMIT: ${env.GIT_COMMIT}"
                echo "HASHLONG: ${HASHLONG}"
                echo "HASHSHORT: ${HASHSHORT}"
                echo "TAG: ${TAG}"
                echo "TAG_HASH: v${TAG_HASH}"
            }
        }
        stage ("Checkout Dependent SCM")
            steps {
                parallel {
                    stage("runxhpl: Checkout")
                    checkout([
                        $class: "GitSCM",
                        branches: [[name: "refs/heads/main"]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [
                               [$class: "RelativeTargetDirectory",
                                relativeTargetDir: "runxhpl"],
                               [$class: "CleanBeforeCheckout"],

                        ]],
                        submoduleCfg: []
                        userRemoteConfigs: [[
                            credentialsID: "buildbot-DeployKey",
                            url: "git@github.com:JustAddRobots/runxhpl.git"
                        ]]
                    ])
                    stage ('runxhpl: Create Git Tag Hash') {
                        steps {
                            script {
                                HASHLONG = sh(
                                    returnStdout: true,
                                    script: """\
                                        git log -1 --pretty=%H --no-merges
                                    """.stripIndent()
                                ).trim()
                                HASHSHORT = sh(
                                    returnStdout: true,
                                    script: """\
                                        git log -1 --pretty=%h --no-merges
                                    """.stripIndent()
                                ).trim()
                                TAG = sh(
                                    returnStdout: true,
                                    script: 'git describe --tags --abbrev=0'
                                ).trim()
                                TAG_HASH = "${TAG}-${HASHSHORT}-${ARCH}"
                            }
                            echo "ARCH: ${env.ARCH}"
                            echo "COMMIT: ${env.GIT_COMMIT}"
                            echo "HASHLONG: ${HASHLONG}"
                            echo "HASHSHORT: ${HASHSHORT}"
                            echo "TAG: ${TAG}"
                            echo "TAG_HASH: v${TAG_HASH}"
                        }
                    }
                    stage ('runxhpl: Build Docker Container') {
                        steps {
                            script {
                                BRANCH = sh(
                                    returnStdout: true,
                                    script: """\
                                        git show-ref |
                                        grep `git rev-parse HEAD` |
                                        awk '{ print \$2 }' |
                                        awk -F/ '{ print \$NF}'
                                    """.stripIndent()
                                    ).trim()
                                env.SERVER = "hosaka.local:5000"
                            }
                            echo "BRANCH: ${BRANCH}"
                            echo "SERVER: ${SERVER}"
                            slackSend(
                                message: """\
                                    STARTED ${env.JOB_NAME} #${env.BUILD_NUMBER},
                                    v${TAG_HASH}
                                    (<${env.BUILD_URL}|Open>)"
                                 """.stripIndent()
                            )
                            sh ("""\
                                    make -C docker/\$ARCH/el-7
                                    SERVER=\$SERVER build push
                                """.stripIndent()
                            )
                        }
                    }
                    stage ('runxhpl: Deploy to Kubernetes Cluster') {
                        steps {
                            script {
                                IMG = """\
                                    ${SERVER}/
                                    runxhpl:${TAG_HASH}
                                """.stripIndent()
                            }
                            sh ("""\
                                python3 /usr/local/bin/runkubejobs
                                -d -t runxhpl
                                -p /var/lib/jenkins/workspace/logs/runxhpl
                                -n all -i ${IMG}
                                """.stripIndent()
                            )
                        }
                    }
                }
            }
        }
    }
}
