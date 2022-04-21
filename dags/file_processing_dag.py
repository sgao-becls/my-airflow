from airflow.decorators import task, dag
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python import BranchPythonOperator
from airflow.operators.python import PythonOperator
from airflow.utils.trigger_rule import TriggerRule

from datetime import datetime
import json

def _file_type_condition_choice(ti):
    fileTypeArgumentStr = ti.xcom_pull('file_type_processing')
    fileTypeArgumentJson = json.loads(fileTypeArgumentStr)
    ti.xcom_push(key='fileTypeArgument', value=fileTypeArgumentStr)
    return fileTypeArgumentJson['type'] + '_processing'

def _prepare_input(ti):
    input={"fileName":"test.fcs","type":1,"experimentId":1}
    return json.dumps(input)

@dag(start_date=datetime(2022, 4, 20),
     schedule_interval='@daily',
     catchup=False, 
     tags=['sgao'])
def file_processing_dag():

    start = DummyOperator(
        task_id='start'
    )

    end = DummyOperator(
        task_id='end',
        trigger_rule=TriggerRule.NONE_FAILED_MIN_ONE_SUCCESS
    ) 

    prepare_input = PythonOperator(
        task_id='input',
        python_callable=_prepare_input
    )      
        
    file_type_processing = DockerOperator(
        task_id='file_type_processing',
        image='file-type-processing:latest',
        container_name='task__file_type_processing',
        auto_remove=True,
        command="{{ ti.xcom_pull('input').replace(' ','') }}",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
    )

    file_type_condition_choice = BranchPythonOperator(
        task_id="file_type_condition_choice", 
        python_callable=_file_type_condition_choice
    )

    fcs_file_processing = DockerOperator(
        task_id='fcs_file_processing',
        image='fcs-file-processing:latest',
        container_name='task__fcs_file_processing',
        auto_remove=True,
        command="{{ ti.xcom_pull('file_type_condition_choice', key='fileTypeArgument').replace(' ','') }}",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge",
    )

    attachment_processing = DockerOperator(
        task_id='attachment_processing',
        image='attachment-processing:latest',
        container_name='task__attachment_processing',
        auto_remove=True,
        command="{{ ti.xcom_pull('file_type_condition_choice', key='fileTypeArgument').replace(' ','') }}",
        docker_url="unix://var/run/docker.sock",
        network_mode="bridge"
    )

    start >> prepare_input >> file_type_processing >>  file_type_condition_choice >> [fcs_file_processing, attachment_processing] >> end


current_dag = file_processing_dag()
