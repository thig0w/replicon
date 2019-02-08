## Synopsis

This is a simple code to extract data information from an excel (with a predefined format) and send it to a new Replicon expense sheet using webservices.

## Motivation

Simplify my expenses reports

## Installation

1. Install Python - https://www.python.org/downloads/ (I am using python 3.7)

2. Check if python is in the path environment variable

    a) Command+r > type "rundll32 sysdm.cpl,EditEnvironmentVariables"

    b) Check if there is somenthing like "setx path "C:\Python\Python27;C:\Python\Python27\Scripts" in the PATH variable

    c) Add it if necessary

3. Open a command window and install the required python modules using the following commands:
```
pip install xlwings reportlab PyPDF2 simplejson requests pypiwin32 pdfkit
```

4. Install de xlwings addon on excel typing the following command on a command window:
```
xlwings addin install
```

5. Garantee that the Project Name Format in your replicon is set to "Name - Code"

	a) Login on your Replicon account
	
	b) Go to settings (engine wheel - upper right corner)
	
	c) Change "Project Name Format" to "Name - Code"

## API Reference

xlwings - http://docs.xlwings.org/en/stable/quickstart.html

## Author
* **Thiago Weidman**

## Contributors
* **Danilo Passos** - The guy who made the worksheet template (Yeap, I stole the idea).
* **Rodrigo Tomazeli** - The Beta tester and "implementer"
* **Manuel Cardoso** - The new features specifier :)
