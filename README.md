# Kube-Sales-DataLake
<div align="center">
  <img src="images/background-image.jpg" alt="Background Image" width="75%"/>
  <br><br>
</div>
This is a Car Sales DataLake implemented using **Python** and **Kubernetes**. This repository includes
both the Kubernetes Infrastructure and Python Source Code for this project.

This project is composed of the following Microservices:
- **Postgres Database**: This is the source of truth for Car Sales
- **Python API**: This is used to interact with the Postgres Database
- **Minio Instance**: This is used as an object store to archive sales data and create a DataLake. For more on Minio, please visit [this](https://www.min.io/) link
- **Python Archiver**: This is used to archive and delete data from the Postgres Database and into the Minio Object Store/Data Lake

The [API](https://hub.docker.com/repository/docker/shahlll/car-sales-api/general) and [Archiver](https://hub.docker.com/repository/docker/shahlll/car-sales-archiver/general) 
Source Code has been Containerized using Docker and the subsequent images have been uploaded to DockerHub. In addition a [Seeder](https://hub.docker.com/repository/docker/shahlll/car-sales-seeder/general) 
test script has been added and containerized to populate the database with test/sample data.


Kubernetes has been used to deploy and manage this system. The following Kubernetes Objects have been used and have been neatly separated into their own folders:
- **ConfigMaps**
- **Deployments**
- **Services**
- **StatefulSets**
- **Jobs** & **CronJobs**

In addition **Secrets** have been used as well. In order to properly deploy use this package the following secrets would have to be manually added
```
S3_ACCESS_KEY: ACCESS_KEY_FOR_MINIO
S3_SECRET_KEY: SECRET_KEY_FOR_MINIO
POSTGRES_PASSWORD: PASSWORD_FOR_POSTGRES
DATABASE_URL: HOST_URL_FOR_POSTGRES
```

Contributions and feedback are more than welcomed. 

When contributing to this project or using it in any way, please do pay attention to: [LICENSE](https://github.com/shahLLL/Kube-Sales-DataLake/tree/main?tab=Apache-2.0-1-ov-file)

☕☕☕**CHEERS AND THANK YOU**☕☕☕

