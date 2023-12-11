# hash:sha256:1c72a47842062e302ce238ce53121a624f18b3bf5c0d033b5abcb4ea20261f13
FROM registry.codeocean.fresnelbio.com/codeocean/py-r:python3.10-R4.2.2-IRkernel-ubuntu22.04

ARG DEBIAN_FRONTEND=noninteractive

ARG GIT_ASKPASS
ARG GIT_ACCESS_TOKEN
COPY git-askpass /

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates=20230311ubuntu0.22.04.1 \
        git=1:2.34.1-1ubuntu1.10 \
        python3-opencv=4.5.4+dfsg-9ubuntu4 \
    && rm -rf /var/lib/apt/lists/*

RUN mamba install -y \
        anndata==0.10.3 \
        gcc==13.2.0 \
        leidenalg==0.9.1 \
        louvain==0.8.0 \
        matplotlib==3.6.3 \
        pandas==1.5.3 \
        python-igraph==0.10.3 \
        r-irkernel==1.3.2 \
        r-rcpp==1.0.10 \
        r-seurat==4.4.0 \
        r-sigclust==1.1.0.1 \
        scanpy==1.9.6 \
    && mamba clean -ya

RUN pip install -U --no-cache-dir \
    anndata2ri==1.3.1 \
    cellbrowser==1.2.3 \
    decoupler==1.5.0 \
    diopy==0.5.5 \
    gget==0.28.2 \
    loompy==3.0.7 \
    nbconvert==7.11.0 \
    omnipath==1.0.8 \
    rpy2==3.5.14 \
    scprep==1.2.3 \
    voyagerpy==0.1.1

RUN pip3 install -U --no-cache-dir \
    dash==2.14.2 \
    dash-bio==1.0.2 \
    plotly==5.18.0

RUN Rscript -e 'remotes::install_version("npsurv", "0.5-0")' \
    && Rscript -e 'remotes::install_version("tidyverse", "2.0.0")'

RUN Rscript -e 'remotes::install_github( \
        "https://github.com/siyao-liu/MultiK")' \
    && Rscript -e 'remotes::install_github( \
        "mojaveazure/seurat-disk", \
        ref = "877d4e18ab38c686f5db54f8cd290274ccdbe295")'

RUN Rscript -e 'options(warn=2); install.packages("BiocManager")'
RUN Rscript -e 'options(warn=2); BiocManager::install(c( \
        "SingleCellExperiment" \
    ))' # Original versions: 1.20.1

ADD "https://github.com/coder/code-server/releases/download/v4.9.0/code-server-4.9.0-linux-amd64.tar.gz" /.code-server/code-server.tar.gz
	
RUN cd /.code-server \
	&& tar -xvf code-server.tar.gz \
	&& rm code-server.tar.gz \
	&& ln -s /.code-server/code-server-4.9.0-linux-amd64/bin/code-server  /usr/bin/code-server
