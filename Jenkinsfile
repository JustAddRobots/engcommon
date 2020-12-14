#!/usr/bin/env groovy

// This Jenkinsfile allows parallel re-builds of dependent packages when the
// 'engcommon' package is tagged for release (or release candidate).
// Add additional package names in the 'parallelBuild' section.

def HASHLONG
def HASHSHORT
def TAG
def TAG_HASH
def MMP
def BRANCH

def DOCKERHOST
def KUBECONFIG

// Requires "Pipeline Utility Steps" and "httpRequest" plugins
def loadProperties() {
    def resp = httpRequest "http://hosaka.local/ini/builder.json"
    def content = resp.getContent()
    echo "${content}"
    def props = readJSON text: "${content}"
    echo "${props}"
    env.DOCKERHOST = props["dockerhost"]
    env.KUBECONFIG = props["kubeconfig"]
}
    
pipeline {
    agent any
    environment {
        ARCH = sh(returnStdout: true, script: 'uname -m').trim()
    }
    stages {
        stage ('Read INI') {
            steps {
                loadProperties()
            }
        }
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
                    TAG_HASH = "${env.TAG}-${env.HASHSHORT}-${env.ARCH}"
                }
                echo "ARCH: ${env.ARCH}"
                echo "COMMIT: ${env.GIT_COMMIT}"
                echo "HASHLONG: ${env.HASHLONG}"
                echo "HASHSHORT: ${env.HASHSHORT}"
                echo "TAG: ${env.TAG}"
                echo "TAG_HASH: v${env.TAG_HASH}"
                slackSend(
                    message: """\
                        STARTED ${env.JOB_NAME} #${env.BUILD_NUMBER}, 
                        v${env.TAG_HASH} (<${env.BUILD_URL}|Open>)
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
    stage('Delete RC Tags') {
        when {
            branch 'main'
        }
        steps {
            script {
                (mmp, _) = "${env.TAG}".tokenize("-") // Major Minor Patch
                env.MMP = "${mmp}"
                echo "MMP: ${env.MMP}"
                withCredentials([usernamePassword(
                    credentialsId: 'github-runxhpl-multibranch-stage',
                    passwordVariable: 'GIT_PASSWORD',
                    usernameVariable: 'GIT_USERNAME'
                )]){
                    sh("""git push --delete https://${env.GIT_USERNAME}:${env.GIT_PASSWORD}@github.com/JustAddRobots/engcommon.git \$(git tag -l "${env.MMP}-rc*")""")
                    sh("""git tag -d \$(git tag -l "${env.MMP}-rc*")""")
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
                    v${env.TAG_HASH}, Took: ${currentBuild.durationString.replace(
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
                    v${env.TAG_HASH}, Took: ${currentBuild.durationString.replace(
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
                    p_TAG_HASH = "${p_TAG}-${p_HASHSHORT}-${env.ARCH}"
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
                }
                echo "BRANCH: ${p_BRANCH}"
                echo "DOCKERHOST: ${env.DOCKERHOST}"
                slackSend(
                    message: """\
                        STARTED PARALLEL ${env.JOB_NAME}.${module} 
                        #${env.BUILD_NUMBER}, v${p_TAG_HASH} (<${env.BUILD_URL}|Open>)
                     """.stripIndent()
                )
                sh ("""\
                        make -C docker/${env.ARCH}/el-7 SERVER=${env.DOCKERHOST} \
                        DOCKERHOST=${env.DOCKERHOST} \
                        ENGCOMMON_BRANCH=${env.GIT_COMMIT} build push
                """)
        }
    }
    stage("${module}: Deploy to Kubernetes Cluster") {
            script {
                IMG = """\
                    ${env.DOCKERHOST}/${module}:${p_TAG_HASH}
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
