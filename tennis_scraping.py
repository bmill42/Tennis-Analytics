import datetime as dt
from airflow import DAG
from airflow.operators.bash import BashOperator

default_args = {
    'owner': 'brian miller',
    'start_date': dt.datetime(2021, 3, 19),
    'retries': 1,
    'retry_delay': dt.timedelta(minutes=5),
}

with DAG('scraping_test_dag',
         default_args=default_args,
         schedule_interval='0 4 * * *',
    ) as dag:

    scrape_operator = BashOperator(task_id='ESPN_scrape',
                                   bash_command='python /Users/brian_miller/Data_Science/tennis_pipeline/scrape_test.py')
