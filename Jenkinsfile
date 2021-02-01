pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Build'){
            steps {
		script {
		    withCredentials([usernamePassword(credentialsId: '46c57260-de63-4ae5-8095-3c760b1e725e', passwordVariable: 'TOKEN', usernameVariable: 'USERNAME')]) {
			def username = env.USERNAME
			def token = env.TOKEN
			sh 'bash ./ci/clang-tidy.sh'
		    }
		}
            }
        }
    }
}
