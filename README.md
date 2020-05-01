## Weather Centric Vehicle Accident Analysis and Risk Reduction Project

This is a quick guide on how to start up the risk analysis program.

Make sure that you are in the root of the repository. Download this zip file:
[WCVAARR.zip](https://drive.google.com/file/d/1delfg9K6svF3hDt_HVnl-deMaFKrrBel/view?usp=sharing)
and unzip it here. Move the json directory into the root of the repository.

Now you can create a virtual directory and then activate it:

```
python -m venv venv

. venv/bin/activate

```

Then you need to install all of our dependencies:

```
pip install -r requirements.txt

```

After that you can run the program:

```
python calculate_risk.py
```

Open a web browser (preferably Mozilla Firefox or Google Chrome) and browse
to http://localhost:8080/. You should be presented with an interface that you
can interact with.

