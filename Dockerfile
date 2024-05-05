FROM quay.io/redhat_msi/qe-tools-base-image:latest

ENV APP_DIR=/hive-claim-flask-app
ENV POETRY_HOME=$APP_DIR
ENV PATH="$APP_DIR/bin:$PATH"

COPY pyproject.toml poetry.lock README.md $APP_DIR/
COPY hive_claim_flask_app $APP_DIR/hive_claim_flask_app/

WORKDIR $APP_DIR

RUN python3 -m pip install --no-cache-dir --upgrade pip --upgrade \
  && python3 -m pip install --no-cache-dir poetry \
  && poetry config cache-dir $APP_DIR \
  && poetry config virtualenvs.in-project true \
  && poetry config installer.max-workers 10 \
  && poetry install

ENTRYPOINT ["poetry", "run", "hive-claim-flask-app"]
