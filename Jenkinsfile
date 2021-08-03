pipeline {
  agent {
    label "metabase"
  }
  stages {
    stage('test') {
      steps {
        sh 'pwd'
        sh 'ls'
        echo env.BRANCH_NAME
      }
    }
    stage('git clone') {
      steps {
        git url:'https://github.com/takashifuruya0/fk_management', branch: env.BRANCH_NAME
       }
    }
    stage("unit test"){
      steps {
        sh 'docker-compose -f docker-compose-test.yaml up'
      }
    }
  }
}