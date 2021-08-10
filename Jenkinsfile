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
            // 変数定義
            image_name = "fk_management_backend_test" + ":" + env.BRANCH_NAME
            echo image_name
            command = 'sed -e "s/build: ./image: '+image_name+'/g" docker-compose-test.yaml > d.yaml'
            echo command
            // 実行
            dockerImage = docker.build image_name
            sh command
            sh 'cat d.yaml'
            sh 'docker-compose -f d.yaml run --rm backend_test'
            // 出力したファイルの下から二行目をチェック。OKならば、もんだいなし
            RES = sh(script: 'tail -n2 tmp | head -n1', returnStdout: true).trim()
            // sh 'docker-compose -f d.yaml down'
            if (RES == "OK") {
              print RES
            } else {
              error RES
            }
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