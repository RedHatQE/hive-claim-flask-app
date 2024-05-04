FROM quay.io/redhat_msi/qe-tools-base-image

RUN curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip" && unzip awscliv2.zip && ./aws/install

COPY hive_claim_flask_app/ /hive-claim-flask-app/hive_claim_flask_app/
COPY pyproject.toml poetry.lock /hive-claim-flask-app/
WORKDIR /hive-claim-flask-app
RUN python3 -m pip install pip --upgrade \
  && python3 -m pip install poetry \
  && poetry config cache-dir /hive-claim-flask-app \
  && poetry config virtualenvs.in-project true \
  && poetry config installer.max-workers 10 \
  && poetry install

ENTRYPOINT ["poetry", "run", "python", "app/app.py"]
