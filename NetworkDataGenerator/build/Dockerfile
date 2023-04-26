# Template Dockerfile for building 'registry.risc-software.at/common/dotnet-template/builder'
# To update, run:
#   podman build -t registry.risc-software.at/common/dotnet-template/builder:latest .
#   podman push registry.risc-software.at/common/dotnet-template/builder
# To test, run:
#   podman run -it --rm --privileged -v "${PWD}:/src" registry.risc-software.at/common/dotnet-template/builder:latest sh
FROM mcr.microsoft.com/dotnet/sdk:7.0-alpine3.17
# Install and configure buildah / podman
RUN apk add --no-cache buildah podman \
    && sed -i -e 's|^#mount_program|mount_program|g' /etc/containers/storage.conf