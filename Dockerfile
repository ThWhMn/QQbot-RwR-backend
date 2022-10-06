FROM python:3.8.0
COPY ./ ./
# RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
RUN pip install --find-links=./data/packs -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
CMD [ "python", "app.py" ]
EXPOSE 7777
