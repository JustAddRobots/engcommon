#!/usr/bin/env groovy

// This Jenkinsfile allows parallel re-builds of dependent packages when the
// 'engcommon' package is tagged for release (or release candidate).
// Add additional package names in the 'parallelBuild' section.

def HASHLONG
def HASHSHORT
def TAG
def TAG_HASH
def BRANCH

def DOCKERHOST
def KUBECONFIG

// Requires "Pipeline Utility Steps" plugin
node {
    props = readProperties file: "builder.ini"
    DOCKERHOST = props["buildhost"]
    KUBECONFIG = props["kubeconfig"]
}
    
pipeline {
    agent any
    environment {
        ARCH = sh(returnStdout: true, script: 'uname -m').trim()
        //KUBECONFIG = '/opt/kube/config'
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
                        v${TAG_HASH} (<${env.BUILD_URL}|Open>)
                     """.stripIndent()
                )
            }
        }
        stage("Start Parallel Dependent Pipelines") {
            failFast true
            parallel {
                stage('Start Builds') {
                    steps {
                        parallelBuild("runxhpl")
                    }
                }
            }
        }
    }
    post {
        success {
            slackSend(
                color: "good",
                message: """\
                    SUCCESS ${env.JOB_NAME} #${env.BUILD_NUMBER},
                    v${TAG_HASH}, Took: ${currentBuild.durationString.replace(
                        ' and counting', ''
                    )} (<${env.BUILD_URL}|Open>)
                """.stripIndent()
            )
        }
        failure {
            slackSend(
                color: "danger",
                message: """\
                    FAILURE ${env.JOB_NAME} #${env.BUILD_NUMBER},
                    v${TAG_HASH}, Took: ${currentBuild.durationString.replace(
                        ' and counting', ''
                    )} (<${env.BUILD_URL}|Open>)
                """.stripIndent()
            )
        }
    }
}

def parallelBuild(module) {
    // vars specific to the parallel build
    def p_HASHLONG
    def p_HASHSHORT
    def p_TAG
    def p_TAG_HASH
    def p_BRANCH
    def p_SERVER

    // always checkout the 'main' branch for dependents
    stage("${module}: Checkout") {
        checkout([
            $class: "GitSCM",
            branches: [[name: "refs/heads/main"]],
            doGenerateSubmoduleConfigurations: false,
            extensions: [
                   [$class: "RelativeTargetDirectory", 
                    relativeTargetDir: "${module}"],
                   [$class: "CleanBeforeCheckout"],
            ], 
            submoduleCfg: [],
            userRemoteConfigs: [[
                credentialsId: "buildbot-${module}",
                url: "git@github.com:JustAddRobots/${module}.git"
            ]]
        ])
    }
    stage("${module}: Create Git Tag Hash") {
            dir("${module}") {
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
        dir("${module}") {
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
                    //p_SERVER = "hosaka.local:5000"
                    //p_SERVER = ${DOCKERHOST}
                }
                echo "BRANCH: ${p_BRANCH}"
                echo "DOCKERHOST: ${DOCKERHOST}"
                //echo "SERVER: ${p_SERVER}"
                slackSend(
                    message: """\
                        STARTED PARALLEL ${env.JOB_NAME}.${module} 
                        #${env.BUILD_NUMBER}, v${p_TAG_HASH} (<${env.BUILD_URL}|Open>)
                     """.stripIndent()
                )
                sh ("""\
                        make -C docker/${ARCH}/el-7 SERVER=${DOCKERHOST} \
                        ENGCOMMON_BRANCH=${env.GIT_COMMIT} build push
                """)
        }
    }
    stage("${module}: Deploy to Kubernetes Cluster") {
            script {
                IMG = """\
                    ${DOCKERHOST}/${module}:${p_TAG_HASH}
                """
            }
            sh ("""\
                    python3 /usr/local/bin/runkubejobs \
                    -d -t ${module} \
                    -p /var/lib/jenkins/workspace/logs/${module} \
                    -n all -i ${IMG}
                """.stripIndent()
            )
    }
}
