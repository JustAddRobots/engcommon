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
        KUBECONFIG = '/opt/kube/config'
    }
    stages {
        stage('Create Git Tag Hash') {
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
                slackSend(
                    message: """\
                        STARTED ${env.JOB_NAME} #${env.BUILD_NUMBER}, 
                        v${TAG_HASH} 
                        (<${env.BUILD_URL}|Open>)"
                     """.stripIndent()
                )
            }
        }
        stage("Start Parallel Dependent Pipelines") {
            parallel {
                stage('Start Builds') {
                    steps {
                        parallelBuild("runxhpl")
                    }
                }
            }
        }
    }
}

def parallelBuild(module) {
    def p_HASHLONG
    def p_HASHSHORT
    def p_TAG
    def p_TAG_HASH
    def p_BRANCH
    def p_SERVER

    stage("${module}: Checkout") {
        checkout([
            $class: "GitSCM",
            branches: [[name: "refs/heads/master"]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [
                   [$class: "RelativeTargetDirectory", 
                    relativeTargetDir: "${module}"],
                   [$class: "CleanBeforeCheckout"],
            ], 
            submoduleCfg: [],
            userRemoteConfigs: [[
                credentialsId: "buildbot-runxhpl",
                url: "git@github.com:JustAddRobots/${module}.git"
            ]]
        ])
    }
    stage("${module}: Create Git Tag Hash") {
        dir("${module}")
        steps {
            script {
                p_HASHLONG = sh(
                    returnStdout: true, 
                    script: """\
                        git log -1 --pretty=%H --no-merges
                    """.stripIndent()
                ).trim()
                p_HASHSHORT = sh(
                    returnStdout: true, 
                    script: """\
                        git log -1 --pretty=%h --no-merges
                    """.stripIndent()
                ).trim()
                p_TAG = sh(
                    returnStdout: true, 
                    script: 'git describe --tags --abbrev=0'
                ).trim()
                p_TAG_HASH = "${p_TAG}-${p_HASHSHORT}-${ARCH}"
            }
            echo "ARCH: ${env.ARCH}"
            echo "HASHLONG: ${p_HASHLONG}"
            echo "HASHSHORT: ${p_HASHSHORT}"
            echo "TAG: ${p_TAG}"
            echo "TAG_HASH: v${p_TAG_HASH}"
        }
    }
    stage("${module}: Build Docker Container") {
        dir("${module}")
        steps {
            script {
                p_BRANCH = sh(
                    returnStdout: true, 
                    script: """\
                        git show-ref | 
                        grep `git rev-parse HEAD` | 
                        awk '{ print \$2 }' | 
                        awk -F/ '{ print \$NF}'
                    """.stripIndent()
                ).trim()
                p_SERVER = "hosaka.local:5000"
            }
            echo "BRANCH: ${p_BRANCH}"
            echo "SERVER: ${p_SERVER}"
            slackSend(
                message: """\
                    STARTED PARALLEL ${env.JOB_NAME}.${module} 
                    #${env.BUILD_NUMBER}, v${p_TAG_HASH} 
                    (<${env.BUILD_URL}|Open>)"
                 """.stripIndent()
            )
            sh ("""make -C docker/\$ARCH/el-7 SERVER=\$SERVER build push""")
        }
    }
    stage("${module}: Deploy to Kubernetes Cluster") {
        steps {
            script {
                IMG = """\
                    ${p_SERVER}/${module}:${p_TAG_HASH}
                """
            }
            sh ("""\
                    python3 /usr/local/bin/runkubejobs 
                    -d -t ${module} 
                    -p /var/lib/jenkins/workspace/logs/${module}
                    -n all -i ${IMG}
                """.stripIndent()
            )
        }
    }
}
