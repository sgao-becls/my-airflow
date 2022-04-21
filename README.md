# Runing airflow in docker

- [ ] install docker-compose
  ```
  pip install docker-compose
  ```
- [ ] check if there is enough memory. (at least 4GB, ideally 8GB)
  ```
  docker run --rm "debian:buster-slim" bash -c 'numfmt --to iec $(echo $(($(getconf _PHYS_PAGES) * $(getconf PAGE_SIZE))))'
  ```
- [ ] Allocate at least 4GB memory for docker engine 
- [ ] Build custom image
  ```
  docker build -t my-airflow .
  ```
- [ ] Set $AIRFLOW_UID
  ```
  echo -e "AIRFLOW_UID=$(id -u)" > .env
  ```
- [ ] Initialize the database 
  ```
  docker-compose up airflow-init
  ```
- [ ] Running airflow
  ```
  docker-compose up 
  ```