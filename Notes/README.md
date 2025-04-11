# Notes
## PicPay Challenge

1st: At first, you will need to open Ubuntu Terminal. Type git clone (link) and click Enter. After, type "cd projects" and then "picpay-jr-devops-challenge". You will be in the projects folder already. Write "code ." to open VSCode. Now you're ready to play with the codes.

Now, focus on finding the errors the codes have. You can start at docker-compose, since the problems of the applications may not be loading firstly because of it.

## First Round: Errors and Issues, how to fix?

To find errors, type "docker compose up" to run docker-compose.yaml. It will show you any errors if they exist in the file.
My problem is that docker is not connecting to the network named frontend, so I need to find a solution, which is either to declare a network inside docker-compose file or to remove the networks line from the web service (according to GPT).
I chose to declare a network.
First, go to the end of the docker code, where you can find "network".
Type: 

frontend: 
driver: bridge
backend: 
driver: bridge

After, type "docker compose up" in the terminal.
It will work, and if you're not lucky it will show you more errors: 
1rst: reader-1  | main.go:5:5: no required module provides package github.com/go-redis/redis: go.mod file not found in current directory or any parent directory; see 'go help modules'
2nd: reader-1  | main.go:6:5: no required module provides package github.com/rs/cors: go.mod file not found in current directory or any parent directory; see 'go help modules'
3rd: Error response from daemon: failed to create task for container: failed to create shim task: OCI runtime create failed: runc create failed: unable to start container process: error during container init: exec: "main.py": executable file not found in $PATH: unknown
The first and second errors are related to a Go project, and the third is related to Python execution inside a container.
The problem with Go is that inside reader container, Go is trying to compile or run my main.go file, but no go.mod was found. Go.mod is required to manage dependencies.
To solve the first two errors, I first installed Go on terminal by the command "sudo snap install go" and typed "go mod init github.com/go-redis/redis" to create a go.mod file and "go get github.com/rs/cors" to create a go.sum file.
Then, I typed docker compose up to check the new modifications, and it was all working. Now, to the last error up to now.
I need to fix python executable file error. 
The problem here is that the main.py file isn't executable, and the problem is inside Dockerfile entrypoint. It is not explicitly calling Python.
I'm going to solve this problem by making main.py executable. 
I need to add #!/usr/bin/env python3 at the top of my main.py according to CHAT GPT and make it executable in my Dockerfile by the command: 

RUN chmod +x main.py 
ENTRYPOINT ["python", "./main.py"]

It will tell Docker to treat main.py like a script.
GPT also made me be sure if the main.py was copied into the Docker image by the command COPY . .
The Dockerfile doesn't need CMD ["python"] if there's entrypoint, so I'm going to delete it. Also, ADD instruction is not needed, so I deleted it.
The python problem is done.
Now I need to solve a new problem: "ModuleNotFoundError: No module named 'redis'". 
It happens because python container is trying to run main.py, which imports redis, but the module is not installed inside the Docker container, according to GPT.
I need to install dependencies via a requirements.txt., inside services/writer/ and make sure the file contains redis in it. 
I also need to update the Dockerfile in services/writer/ to install requirements. 
It was possible by the command "RUN pip install --no-cache-dir -r requirements.txt" right before "RUN chmod +x main.py". 
"I wrote COPY requirements.txt ." right before "RUN pip install --no-cache-dir -r requirements.txt".
The instruction from GPT said to rebuild the image from docker with no cache using the command "docker compose build --no-cache writer" and then running it with "docker compose up writer".
For Go Reader — no required module provides package error, I kind of find out because GPT said go.mod and go.sum needed to be inside reader folder, so I put them in it.
GPT said that I should make sure the Go Dockerfile for reader copies everything, so he gave me a code I used to modify the Dockerfile.
Jumping to the end, after verifying everything as it should be (I'm tired) I must use docker compose build and docker compose up to check if things work, and if they work I guess I've finished everything. Right now I'm gonna sleep and wait for Vitor's response.
Aaaaaand, all finished! Thanks for reading.
Ok, not finished. Let's head to the second part of the challenge.
## Second round: Ports
Now, that I found out there's more to do, I need to know what exatcly. I typed with GPT and found that the links of localhost aren't working. They aren't working because the mapped ports are switched between the writer and reader services.
Writer internal port, which is 8080, should be 8081 instead, while reader internal port, which is 8081, should be 8080.
What I need to do is change writer and reader ports. Writer port goes to 8081 and reader port goes to 8080.
After this, I need to restart the containers by the command:
docker compose down
docker compose up --build
Ok, seems it worked. I need to open localhost 8080 and 8081 in the web to see if it works.
Yes, it worked. When I opened localhost 8080 and 8081 (by the command http://localhost:8081/health), they showed me "up" message in the website page. Although, localhost 50000 did not work.
To solve localhost 5000 problem I first need to know which app the code in services/frontend is running - if React, Express or Nginx. 
I also find out I'm running a static site served by serve, which is great for React builds or vanilla HTML/JS, according to GPT.
But there seems to be a little issue within my Dockerfile that is stopping it from running correctly, which is the line 6: CMD "serve".
According to GPT, it just passes a string, which doesn't get interpreted as an executable command by Docker properly.
So, I need to update CMD to an **array form**. To do that, I replace the line 6 with: CMD ["serve", ".", "-l", "5000"]. 
With that replacement, Docker will properly run "serve" on the current directory(.) and bind it to port 5000, which is what I'm exposing, according to GPT.
Now, I need to rebuild and run by using the commands:
docker compose down
docker compose build web
docker compose up
Now, I try to run localhost 5000 in website, and... IT WORKED!

Another recommendation from GPT was to change docker-compose.yaml reids by just adding networks and backend, by typing: 
"redis:alpine":
networks:
 - backend
 after "image:".

 GPT said to do that to assign Redis to the backend network explicitly, because writer and reader use it.
 Also, GPT gave me a warn to make sure reader and writer need to talk to Redis, so they should both be in the backend network.
 GPT said web(frontend) needs to talk to reader, so reader should be in both frontend and backend(if needed). So, I'll update reader to connect both as indicated by GPT.
 It was easy, because I just needed to add "- backend" to reader: networks.

 Now I'm just making sure everything's working. Seems that **Redis connection test** did not say "hello" and network connectivity between services also did not. 
 Redis is not working. It is not reachable from writer. Writer is trying to connect to a Redis host named "redis", but that hostname doesn't resolve in Docker's internal DNS. But, in my docker-compose.yaml, redis is typed wrongly.
 It was written as "reids", not redis. I just changed and typed curl -X POST -d "hello" http://localhost:8081/write in the terminal to test it.
 It didn't work, because I first need to "docker compose down" then "docker compose up --build" to restart docker compose.
 Now it worked and showed me {"message": "Data saved"}. Now I typed curl "http://localhost:8080/data" and got "hello" as what I planned. God is good, amen!
 Now, for "network connectivity between services" not working. I need reader and writer to talk to each other, but they must share a common network. While testing the command docker exec "-it docker-compose.yaml ping redis", GPT said, about the error "OCI runtime exec failed: exec failed: unable to start container process: exec: "ping": executable file not found in $PATH: unknown" that the ping command isn't nstalled in the writer container.
 So I executed python via terminal by the command "docker exec -it writer python. It send me to python terminal.
 Here is the list of commands I used to test connection of Redis inside python:

 import redis
 r = redis.Redis(host="redis", port=6379)
 r.set("testkey", "hello")
 It said true, then I typed
 r.get("testkey")

 and got b'hello, so it proves I'm connected to Redis.
 I tried sending a POST request to writer with "curl -X POST -d "hello world" http://localhost:8081/write" and it worked. I checked it using "curl http://localhost:8080/data".
 After testing everything and getting to know everything works, I need now to automate with a "health check script".
 First, I need to create a health_check.sh file to run the health check script properly, paste
 #!/bin/bash

echo "Writer -> POST /write"
curl -X POST -d "hello world" http://localhost:8081/write
echo -e "\n"

echo "Reader -> GET /data"
curl http://localhost:8080/data
echo -e "\n"

echo "Frontend should be live at: http://localhost:5000"

inside of it and make it executable by typing 
chmod +x health_check.sh
via terminal.
Didn't work, "chmod: cannot access 'health_check.sh': No such file or directory". Found that it wasn't in the same directory as docker-compose.yaml, so I just moved it through directories.
Then, executed the command "./health_check.sh and it worked.

## Extra: New health_check.sh with HTTP Status Validation

Just to upgrade the code as it is said in the challenge, I am going to make a little adjustment to make health check have HTTP status validation.
For that, I am going to replace the content of health_check.sh with the following: 

#!/bin/bash

# Colors for the terminal
GREEN="\033[0;32m"
RED="\033[0;31m"
RESET="\033[0m"

check_status() {
    if [ $1 -eq 200 ] || [ $1 -eq 201 ]; then
        echo -e "${GREEN}[✔] $2 is working!${RESET}"
    else
        echo -e "${RED}[✘] $2 failed (status $1)${RESET}"
    fi
}

echo "▶️ Testing Writer -> POST /write"
response=$(curl -s -o /dev/null -w "%{http_code}" -X POST -d "hello world" http://localhost:8081/write)
check_status $response "Writer"

echo "▶️ Testing Reader -> GET /data"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/data)
check_status $response "Reader"

echo "▶️ Testing Reader -> GET /health"
response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8080/health)
check_status $response "Reader /health"

echo "▶️ Frontend should be available at: http://localhost:5000"

I don't really understand 100% of the code that was generated from GPT, yet.

Now I'll test again with

docker compose up --build

give execution permission with

chmod +x health_check.sh

and run with

./health_check.sh

and what I got is:
[✔] Writer is working!
▶️ Testing Reader -> GET /data
[✔] Reader is working!
▶️ Testing Reader -> GET /health
[✔] Reader /health is working!
▶️ Frontend should be available at: http://localhost:5000

So, I guess it's all done.


 Apparently everything responses well from both endpoints, and also data is consistent.
 Tip: Always restart container with docker compose down and docker compose up --build when changing network configs.



1st: Others
2nd: Group
3rd: Owner
Chmod: File permission
chmod 750 main.py = Eu (owner) recebo permissão 7 de fazer qualquer coisa
Perm 5 Leitura e execução
Perm 0 No permission
Docker é linguagem imperativa
System D
Estudar muito Docker
Kernel do Linux roda em qualquer coisa (tipo em um iPad de primeira geração)
Docker usa o System D do Linux

Node
Go
Python

O container é um mundo controlado por alguém que faz alguma coisa para aquela pessoa e está programado para fazer algo que a pessoa quer.
Exemplo: A Alexa é o orquestrador do Dockerfile e a lâmpada que acende e apaga é o container. São automações.
O bash é um comando com começo, meio e fim. Já o container não tem fim, pois ele não acaba.

As portas do localhost existem do 1 até 9999, mas existem convenções, que geralmente usam portas localhost 8080 e 8081.

Git add cria um pacote