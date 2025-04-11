FROM golang:1.23@sha256:5b787a3adda03343e666f0a35b15858664a96e87cf872c60ea2af077f9c98b41
WORKDIR /go/src/github.com/PicPay/picpay-jr-devops-challenge/services/go
ADD . /go/src/github.com/PicPay/picpay-jr-devops-challenge/services/go

WORKDIR /app

COPY . .

ENV GOTOOLCHAIN=auto

RUN go mod tidy
RUN go get github.com/go-redis/redis
RUN go build -o main .

EXPOSE 8080
CMD ["go","run","main.go", "./main"]