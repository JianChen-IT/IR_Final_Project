# Information retrieval - Final Project
This repository contains the delivery of the Information Retrieval Final Project, subject taught in the UPF (1st Term 2020). The content of this report contains the recommended structure provided by the Project Guidelines.

## Want to run the Search Engine?

The search engine has a database a file that must be located and named `other-outputs/tweets_US_Election_2020.json`. Otherwise, it will not work. However, if you collect the data, this file will be created automatically in the data collection. If you want to run the search engine, make sure that the file is created.

*To run the Search Engine*, here you have the minimum lines of code to do the task:

```python
from search_engine.search_engine import SearchEngine

print("Insert your query:\n")
query = input()
search_engine.run(query).query("score > 0").head(20)
```

*To run it with Word2Vec do:*

```python
from search_engine.search_engine import SearchEngine

search_engine.ranking_system.change_user_input(2) # Add this line to change the mode to Word2Vec
print("Insert your query:\n")
query = input()
search_engine.run(query).query("score > 0").head(20)
```

*To run our custom score:*

```python
from search_engine.search_engine import SearchEngine

print("Insert your query:\n")
query = input()
search_engine.run_custom_score(query).query("score > 0").head(20)
```

*To collect data:*

Open `search_engine.py` and set the flag `GET_TWEETS` to 1.

*To control the size of the data collected:*

Open `search_engine.py` and modify the variable `stop_condition` in the `initialize` method. In the code is set to 10k, but when running our Notebooks, we collected 100K

*To read the JSON completely:*

Open `search_engine.py` and set the flag `GET_ALL` to 1.

*To control the size of data read from the JSON:*

Open search_engine.py and modify the variable stop_condition in the setup method. In the code is set to 1k, but when running our notebooks we put `GET_ALL = 1`