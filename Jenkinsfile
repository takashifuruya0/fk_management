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
    stage("build"){
      steps {
        script {
            version = "fk_management_backend_test" + ":" + env.BRANCH_NAME
            echo version
            dockerImage = docker.build version
            sh 'sed -e "s/build: ./image: ${version}/g" docker-compose-test.yaml > d.yaml'
            sh 'cat d.yaml'
            sh 'docker-compose -f d.yaml up '
        }
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