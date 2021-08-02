pipeline {
  agent {
    label "metabase"
  }
  stages {
    stage('test') {
      steps {
        sh 'pwd'
        echo $BRANCH_NAME
      }
    }
  }
}