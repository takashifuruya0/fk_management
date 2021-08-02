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
  }
}