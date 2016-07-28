FROM pymssql/pymssql
MAINTAINER Philipp Adelt <autosort-github@philipp.adelt.net>
 
RUN echo "ls -l " >> ~/.bashrc
ADD runner.py /runner.py
ADD query.sql /query.sql
CMD ["python", "runner.py"]
