FROM mcr.microsoft.com/playwright/python:v1.51.0

WORKDIR /app

ENV TZ=Asia/Ho_Chi_Minh
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

RUN mkdir -p /app/snapshot

COPY requirements.txt /app/
RUN pip install --upgrade pip --no-cache-dir --root-user-action=ignore \
    && pip install --no-cache-dir -r requirements.txt --root-user-action=ignore

RUN playwright install --with-deps \
    && rm -rf /root/.cache

COPY . /app/

RUN chmod +x /app/entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]