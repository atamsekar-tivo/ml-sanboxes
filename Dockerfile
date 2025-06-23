FROM python:3.11-slim

# Install build tools, then remove after pip install
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential git && \
    rm -rf /var/lib/apt/lists/* && \
    pip install --upgrade pip && \
    pip install --no-cache-dir jupyterlab pandas numpy matplotlib scikit-learn seaborn xgboost lightgbm tensorflow && \
    apt-get purge -y build-essential git && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*

# Set up a user with the same UID/GID as the host (default to 1000)
ARG NB_UID=1000
ARG NB_GID=1000
RUN groupadd -g $NB_GID jupyteruser \
    && useradd -m -u $NB_UID -g $NB_GID -s /bin/bash jupyteruser

RUN mkdir -p /tf/notebooks && chown -R jupyteruser:jupyteruser /tf/notebooks

USER jupyteruser
ENV HOME=/tf/notebooks
WORKDIR /tf/notebooks

CMD ["jupyter", "lab", "--ip=0.0.0.0", "--no-browser", "--ServerApp.token=", "--ServerApp.password=", "--ServerApp.allow_origin=*", "--ServerApp.allow_root=True", "--ServerApp.allow_remote_access=True", "--ServerApp.disable_check_xsrf=True", "--ServerApp.trust_xheaders=True", "--notebook-dir=/tf/notebooks"]
