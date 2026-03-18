FROM ubuntu:24.04

ENV DEBIAN_FRONTEND=noninteractive

# Install sudo (needed by bootstrap scripts when not running as root).
RUN apt-get update && apt-get install -y sudo && rm -rf /var/lib/apt/lists/*

# Create non-root user with password-less sudo.
ARG USERNAME=dev
ARG USER_UID=1001
ARG USER_GID=$USER_UID
RUN groupadd --gid $USER_GID $USERNAME \
    && useradd --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME

# Copy and run bootstrap scripts as root.
COPY repos/bootstrap /tmp/bootstrap
WORKDIR /tmp/bootstrap
RUN bash ./run/bootstrap.sh

# Clean up.
RUN rm -rf /tmp/bootstrap
WORKDIR /home/dev
