# Build the Docker container
build:
	docker build -t djaisp-backend .

# Run the Docker container and enter a bash shell
run:
	docker run -it --rm -p 8989:8989 djaisp-backend

# Shortcut to build, run, install, and start the app in development mode
start: build run