# https://github.com/ckan/ckanext-dcat/pull/326

# https://raw.githubusercontent.com/ckan/ckan-docker-base/refs/heads/main/ckan-2.11/Dockerfile
ARG CKAN_VERSION=2.11

FROM --platform=linux/amd64 ckan/ckan-base:${CKAN_VERSION} AS builder

# Install any extensions needed by your CKAN instance
# See Dockerfile.dev for more details and examples

USER root

### ckanext-dcat ###
ARG CKANEXT_DCAT_VER=v2.4.2
ENV CKANEXT_DCAT_VER=${CKANEXT_DCAT_VER}
RUN  pip3 install -e git+https://github.com/ckan/ckanext-dcat.git@$CKANEXT_DCAT_VER#egg=ckanext-dcat && \
    pip3 install -r https://raw.githubusercontent.com/ckan/ckanext-dcat/$CKANEXT_DCAT_VER/requirements.txt

### Scheming ###
RUN pip install -e "git+https://github.com/ckan/ckanext-scheming.git#egg=ckanext-scheming"

# Apply any patches needed to CKAN core or any of the built extensions
COPY --chown=ckan-sys:ckan-sys patches ${APP_DIR}/patches

USER ckan

RUN for d in $APP_DIR/patches/*; do \
        if [ -d $d ]; then \
            for f in `ls $d/*.patch | sort -g`; do \
                cd $SRC_DIR/`basename "$d"` && echo "$0: Applying patch $f to $SRC_DIR/`basename $d`"; patch -p1 < "$f" ; \
            done ; \
        fi ; \
    done

FROM --platform=linux/amd64 ckan/ckan-base:${CKAN_VERSION} AS final
LABEL description="CKAN Docker image with HealthDCAT-AP profile and Scheming extension"

ENV CKAN__PLUGINS="dcat dcat_json_interface \
  scheming_datasets structured_data \
  image_view text_view \
  datatables_view datastore \
  datapusher envvars"

USER root

# Copy installed extensions from builder stage
COPY --from=builder --chown=ckan-sys:ckan-sys /srv/app/src/ /srv/app/src/
COPY --from=builder --chown=ckan-sys:ckan-sys /usr/local/lib/python3.10/site-packages/ /usr/local/lib/python3.10/site-packages/

# Copy custom initialization scripts
COPY --chown=ckan-sys:ckan-sys docker-entrypoint.d/* /docker-entrypoint.d/

USER ckan
