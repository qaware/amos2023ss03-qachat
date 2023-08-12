FROM python:3.10

#RUN mkdir -p QAChat/Data_Processing
#WORKDIR /QAChat/Data_Processing

#pip install --upgrade pip

COPY requirements.txt .
RUN pip install --verbose -r requirements.txt
RUN rm -f requirements.txt

RUN python -m spacy download xx_ent_wiki_sm
RUN python -m spacy download de_core_news_sm

COPY setup.py .
RUN python setup.py
RUN rm -f setup.py

ENV PYTHONPATH=$PYTHONPATH:/

ENTRYPOINT ["python", "/QAChat/Data_Processing/main.py"]

