FROM kieranpotts/devcontainer:latest

ENV DEBIAN_FRONTEND=noninteractive
ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=1000

RUN USER_UID=${USER_UID:-1000} USER_GID=${USER_GID:-1000} && \
    groupadd --gid ${USER_GID} ${USERNAME} && \
    useradd --uid ${USER_UID} --gid ${USER_GID} -m -s /bin/bash ${USERNAME} && \
    mkdir -p /workspace && \
    chown ${USERNAME}:${USERNAME} /workspace

USER ${USERNAME}
WORKDIR /workspace
