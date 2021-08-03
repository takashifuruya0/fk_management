pipeline {
  agent {
    label "metabase"
  }
  stages {
    stage('test') {
      steps {
        sh 'pwd'
        echo env.BRANCH_NAME
      }
    }
    stage("unit test"){
      steps {
        sh 'docker-compose -f docker-compose-test.yaml up'
      }
    }
  }
}