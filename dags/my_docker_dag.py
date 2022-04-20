from airflow.decorators import task, dag
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.bash_operator import BashOperator

from datetime import datetime

@dag(start_date=datetime(2022, 4, 20),
     schedule_interval='@daily',
     catchup=False)
def docker_dag():

    start_dag = DummyOperator(
        task_id='start_dag'
    )

    end_dag = DummyOperator(
        task_id='end_dag'
    )        

    show_date_step = BashOperator(
        task_id='show_date_step',
        bash_command='date'
    )
        
    echo_step = DockerOperator(
        task_id='echo_step',
        image='python:3.8.13-slim-buster',
        container_name='task___echo_step',
        auto_remove=True,
        command="echo 'hello world!!'",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
    )

    sleep_step = DockerOperator(
        task_id='sleep_step',
        image='python:3.8.13-slim-buster',
        container_name='task___sleep_step',
        auto_remove=True,
        command="/bin/sleep 10",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
    )

    done_step = BashOperator(
        task_id='done_step',
        bash_command='echo "Done!!"'
    )

    start_dag >> show_date_step 
    show_date_step >> echo_step >> done_step
    show_date_step >> sleep_step >> done_step
    done_step >> end_dag

current_dag = docker_dag()