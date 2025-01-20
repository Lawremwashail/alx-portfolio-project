from redis import Redis

# Connect to Redis
redis_client = Redis(host='127.0.0.1', port=6379, db=0)

# Test the connection
try:
    response = redis_client.ping()
    print("Redis connection successful:", response)
except Exception as e:
    print("Redis connection failed:", str(e))

