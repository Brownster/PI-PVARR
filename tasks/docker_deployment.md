# Task 3: Docker Deployment

Goal: provide a functional `docker-compose.yml` file for the media stack that works on both arm64 and amd64 architectures.

## Subtasks
- Create or update a single `docker-compose.yml` defining services such as Sonarr, Radarr, Prowlarr, Jellyfin, and supporting tools.
- Use Docker images that offer multi-arch support (arm64 and amd64).
- Set up volume mounts and environment variables via an `.env` file.
- Document how to launch, stop, and update the stack.
- Test the compose file separately on Raspberry Pi and x86_64 machines.
