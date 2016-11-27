FROM python:onbuild

EXPOSE 8080

CMD ["python","./AsyncProxy.py"]