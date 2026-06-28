# --- Build stage: render the Astro static site for the ziy.one apex ---
FROM oven/bun:1 AS build
WORKDIR /app

# Install deps against the committed lockfile for reproducible builds.
COPY package.json bun.lock ./
RUN bun install --frozen-lockfile

COPY . .

# Apex domain serves at root, not the /ZiyOne GitHub Pages subpath.
ARG ASTRO_BASE=/
ARG ASTRO_SITE=https://ziy.one
ENV ASTRO_BASE=${ASTRO_BASE} ASTRO_SITE=${ASTRO_SITE}
RUN bun run build

# --- Runtime stage: minimal nginx serving the static output ---
# Pulled from ECR mirror, not Docker Hub: the cluster's shared egress IP hits
# Docker Hub's anonymous pull-rate limit (429) on cold pulls. See infra README.
FROM public.ecr.aws/docker/library/nginx:1.27-alpine
COPY deploy/nginx.conf /etc/nginx/nginx.conf
COPY --from=build /app/dist /usr/share/nginx/html

# Run as the prebuilt unprivileged nginx user (uid/gid 101).
USER 101
EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
