package main

import (
    "fmt"
    "github.com/go-redis/redis"
    "github.com/rs/cors"
    "log"
    "net/http"
    "os"
)

var redisClient *redis.Client

func init() {
    fmt.Println("Service is initializing...")

    redisHost := getEnv("REDIS_HOST", "redis")
    redisPort := getEnv("REDIS_PORT", "6379")

    redisClient = redis.NewClient(&redis.Options{
        Addr: redisHost + ":" + redisPort,
    })

    _, err := redisClient.Ping().Result()
    if err != nil {
        log.Fatalf("Could not connect to Redis: %v", err)
    }
}

func main() {
    fmt.Println("Service started.")

    mux := http.NewServeMux()

    mux.HandleFunc("/health", func(w http.ResponseWriter, r *http.Request) {
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }
        fmt.Fprint(w, "up")
    })

    mux.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
        if r.Method == "OPTIONS" {
            w.WriteHeader(http.StatusOK)
            return
        }

        val, err := redisClient.Get("SHAREDKEY").Result()
        if err == redis.Nil {
            http.Error(w, "Key not found", http.StatusNotFound)
            return
        } else if err != nil {
            http.Error(w, fmt.Sprintf("Redis error: %v", err), http.StatusInternalServerError)
            return
        }

        fmt.Fprint(w, val)
    })

    handler := cors.New(cors.Options{
        AllowedOrigins: []string{"*"},
        AllowedHeaders: []string{"*"},
    }).Handler(mux)

    log.Fatal(http.ListenAndServe(":8080", handler))
}

func getEnv(key, fallback string) string {
    if value, ok := os.LookupEnv(key); ok {
        return value
    }
    return fallback
}