package main

import (
	"context"
	"fmt"
	"log"
	"net/http"

	"github.com/go-redis/redis/v8"
	"github.com/rs/cors"
)

var ctx = context.Background()

func init() {
	fmt.Println("Service is initializing...")
}

func main() {
	fmt.Println("Service started.")

	redis_host := "redis"
	redis_port := "6379"
	mux := http.NewServeMux()

	mux.HandleFunc("/health", func(writer http.ResponseWriter, request *http.Request) {
		if request.Method == "OPTIONS" {
			writer.WriteHeader(http.StatusOK)
			return
		}
		fmt.Fprintf(writer, "up")
	})

	mux.HandleFunc("/data", func(writer http.ResponseWriter, request *http.Request) {
		fmt.Println("Tentando conectar ao Redis...")
		client := redis.NewClient(&redis.Options{
			Addr: redis_host + ":" + redis_port,
		})

		key, err := client.Get(ctx, "SHAREDKEY").Result()
		if err == redis.Nil {
			fmt.Println("Chave não encontrada no Redis.")
			http.Error(writer, "Key not found", http.StatusNotFound)
			return
		} else if err != nil {
			fmt.Printf("Erro ao conectar ao Redis: %v\n", err)
			http.Error(writer, "Error connecting to Redis: "+err.Error(), http.StatusInternalServerError)
			return
		}

		fmt.Printf("Chave encontrada: %s\n", key)
		fmt.Fprintf(writer, key)
	})

	handler := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedHeaders: []string{"*"},
	}).Handler(mux)

	log.Fatal(http.ListenAndServe(":8080", handler))
}
