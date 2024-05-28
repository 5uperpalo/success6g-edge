# sort imports
isort --quiet inference_model notebooks
# Black code style
black inference_model notebooks
# flake8 standards
flake8 inference_model notebooks --max-complexity=10 --max-line-length=127 --ignore=E203,E266,E501,E722,E721,F401,F403,F405,W503,C901,F811
# mypy
mypy inference_model --ignore-missing-imports --no-strict-optional