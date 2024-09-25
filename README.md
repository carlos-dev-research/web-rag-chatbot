## Installation and Dependencies Setup
- Environment managed with conda
- Tested on Python 3.10

### Install Python Packages

```bash
#!/bin/bash
pip install jupyterlab
pip install torch torchvision torchaudio
pip install --ignore-installed blinker
pip install transformers soundfile librosa ollama Flask ffmpeg
pip install llama-index-core llama-index-readers-file llama-index-llms-ollama llama-index-embeddings-huggingface
pip install mysql-connector-python
pip install pytest
pip install pytube
pip install bcrypt
```

### Starting the Mysql Services
- On Windows CMD
```CMD
REM Get last mysql docker image
docker pull mysql:latest

REM Run the docker container, mount storage for persistency of Data, and copy init.sql to setup database
docker run --name service-sql -v "%CD%/db-mysql:/var/lib/mysql" -v "%CD%/init.sql:/docker-entrypoint-initdb.d/init.sql" -e MYSQL_ROOT_PASSWORD=root_password -p 3306:3306 -d mysql:latest

REM command to interact with database if needed
docker exec -it service-sql mysql -u root -p
```

