FROM quay.io/redhat_msi/qe-tools-base-image

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install

ENV APP_DIR=/hive-claim-flask-app

COPY hive_claim_flask_app/ $APP_DIR/hive_claim_flask_app/
COPY pyproject.toml poetry.lock /hive-claim-flask-app/
WORKDIR $APP_DIR
RUN python3 -m pip install --no-cache-dir --upgrade pip --upgrade \
  && python3 -m pip install --no-cache-dir poetry \
  && poetry config cache-dir $APP_DIR \
  && poetry config virtualenvs.in-project true \
  && poetry config installer.max-workers 10 \
  && poetry install

ENTRYPOINT ["poetry", "run", "python", "hive_claim_flask_app/app.py"]
