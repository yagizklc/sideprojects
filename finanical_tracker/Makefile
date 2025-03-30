IMAGE_NAME ?= ghcr.io/yagizklc/financial-tracker/financial-tracker:latest
CONTAINER_NAME ?= financial-tracker
ADMIN_PASSWORD ?= $(shell cat .env)

.PHONY: build run pull push clean

build:
	@echo "Building Docker image: $(IMAGE_NAME)"
	docker build \
	-t $(IMAGE_NAME) \
	.

# Combined run target that handles both modes
run: build
	@echo "Starting the application..."
	docker run \
		-p 8000:8000 \
		--rm \
		--secret id=ADMIN_PASSWORD \
		--name $(CONTAINER_NAME) \
		$(IMAGE_NAME)

pull:
	@echo "Login to GitHub Container Registry..."
	docker login ghcr.io

	@echo "Pulling Docker image: $(IMAGE_NAME)"
	docker pull $(IMAGE_NAME)

push: build
	@echo "Pushing Docker image: $(IMAGE_NAME)"
	docker push $(IMAGE_NAME)

clean:
	@echo "Cleaning up local Docker images..."
	docker rmi -f $(IMAGE_NAME) || true
