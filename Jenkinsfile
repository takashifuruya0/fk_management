pipeline {
  agent {
    label "metabase"
  }
  stages {
    stage('test') {
      steps {
        sh 'pwd'
        sh 'ls'
        sh 'who'
        sh 'hostname'
        echo env.BRANCH_NAME
      }
    }
    stage ('create envfile') {
      steps {
        script {
          withCredentials([file(credentialsId: 'fk-management-env-develop', variable: 'ENVFILE')]) {
            sh 'mkdir -p env'
            sh 'cp $ENVFILE env/'
          }
        }
      }
    }
    stage("unit test"){
      steps {
        sh '/usr/local/bin/docker-compose -f docker-compose-test.yaml up --build'
      }
    }
  }
  //　事後処理
  post {
    always {
      cleanWs()
    }
  }
}