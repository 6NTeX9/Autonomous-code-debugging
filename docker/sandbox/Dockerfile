FROM node:20-alpine

# Secure isolated sandbox container for repository execution
RUN apk add --no-cache git bash python3 py3-pip make g++

# Create non-root unprivileged execution user
RUN addgroup -S appgroup && adduser -S appuser -G appgroup

WORKDIR /workspace

USER appuser

CMD ["sh"]
