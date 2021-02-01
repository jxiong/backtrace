pipeline { 
    agent any 
    options {
        skipStagesAfterUnstable()
    }
    stages {
        stage('Build') { 
            steps { 
                sh 'echo build...' 
            }
        }
        stage('Test'){
            steps {
                sh 'echo testing...'
            }
        }
    }
}
