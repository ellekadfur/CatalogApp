# Catalog App

This project demonstrates how to use set up a python server using flask,
sqlalchemy, and the postgres database management system. The database used is
for categories. There are 3 tables in the data base. The
Item table hold the items that belong to a category. The
Category table includes the category themselves. The User table includes all the users who signed up. The app is built using Facebook Login API. The project will use the data base to allow users to store items in various categories.


## Getting Started

These instructions will help you build the project on your own machine.
To start on this project, you'll need database software (provided by a
Linux virtual machine) and the data to analyze. Please see prerequisites
and links to down load what you need to get started.

### Installing & Prerequisites

Below are listed the software and tools you need to install and how to
install them.

Terminal application
Terminal provides a command line interface to control the UNIX-based operating system that lurks below macOS (or Mac OS X). Here's everything you need to know about Terminal, and what it can do for you and your Mac. Continue reading at
link here to know more about terminal:
http://www.macworld.co.uk/feature/mac-software/how-use-terminal-on-mac-3608274/


The data is in the project folder. Please be sure to unzip the data once you
download it. Then at the command line, to load the data, use the command
python3 catalogdb.py. This will create the database for you.

### Building the Project

0. You should already have the database created if not, at the command line,
to load the data, type python3 catalogdb.py.
1. Then you have to add some categories by typing python3 createcategories.py
2. then type python3 catalog.py to run the app
3. Then to go browser and type:http://0.0.0.0:8000/categories/ to go to home page
4. Use the web app!
5. If you want to delete the data base entirely and start over. You have to
delete the catalog.db file from the folder. But if you do this, that means
you have to go through steps 0-4 again.
type rm catalog.db
BE VERY CAREFUL NOT TO DELETE INCORRECT FILES, you will have to download
zip project again.


Any issues email me ileviathanx@gmail.com.

## Running the tests

I didn't create any special tests for this project.

### And coding style tests

Followed pep8 coding style because Udacity said so.

## Deployment

Add additional notes about how to deploy this on a live system

## Built With

* [Python3](https://www.python.org/download/releases/3.0/) - latest version of
 python
* [Flask](http://flask.pocoo.org) - a microframework for Python
* [sqlalchemy](https://www.sqlalchemy.org) - the Python SQL toolkit and Object
 Relational Mapper

## Contributing

There's no need to contribute.

## Versioning

This is and will be the only version.

## Authors

* **ileviathanx@gmail.com** - *Initial work*

## License

This project is licensed under the MIT License - see
(https://opensource.org/licenses/MIT) file for details

## Acknowledgments

* Udacity & Udacity Friends

## Question?
*  When to use single quotes and when to use double quotes? I believe there
 are time when we can't use double quotes, so why ever use double quotes
 in python?

* I couldn't get Google API to work it seems a lot of people had that problem
https://productforums.google.com/forum/#!msg/gmail/Ig7CN68yG9k/-dSigJ7qOQAJ
