# Python Labs Project

This repository contains the completed assignments for 7 Python labs, covering various web frameworks, database technologies, and development practices.

## Lab Summaries

### Lab 1: FastAPI + SQLAlchemy
This lab focuses on building a RESTful API web application using the FastAPI framework and SQLAlchemy ORM. Key aspects include:
* Generating HTML content on the server and sending it to the client.
* Storing data in a relational database (e.g., SQLite) with at least 3 entities.
* Implementing CRUD operations (create, read, update, delete) for at least one entity.
* Utilizing SQLAlchemy ORM for data access.
* Incorporating two user roles: administrator and regular user.
* Modifying default OpenAPI documentation.

### Lab 2: PostgreSQL
This lab involves migrating data from a previous project to PostgreSQL, maintaining core web application functionality, and adding new features using PostgreSQL and the Psycopg library. The lab covers working with:
* The Psycopg module for connecting to PostgreSQL.
* Creating databases and tables.
* Adding, selecting, updating, and deleting data.

### Lab 3: MongoDB
This lab focuses on migrating data to MongoDB from a previous project, preserving existing functionality, and expanding it through MongoDB and the PyMongo library. Topics include:
* Understanding MongoDB's data structure and documents.
* Installation and administration of the database.
* Adding, selecting, and filtering data.
* Implementing pagination, sorting, and indexing.
* Using aggregate functions.

### Lab 4: Django (Setup, URLs, Views, Templates)
This lab introduces the Django framework, covering its installation, configuration, routing, and view development with templates. Since database connection is not covered, the lab uses a fixed set of data. Covered topics:
* Setting up a Django project and application.
* Handling requests and defining routes using `path` and `re_path`.
* Working with `HttpRequest` and `HttpResponse`.
* Managing URL parameters, query string parameters, and nested routes.
* Implementing redirection, status codes, and JSON responses.
* Working with cookies.

### Lab 5: Django (Forms, Models)
Building upon the previous Django lab, this assignment focuses on forms, data validation, database connectivity, and working with models. Key areas include:
* Handling form submissions and defining Django forms (e.g., `forms.Form`, `ModelForm`).
* Using various field types and widgets.
* Configuring forms and fields.
* Implementing data validation.
* Connecting to databases and performing database migrations.
* Creating and interacting with models, including CRUD operations.
* Querying data using QuerySet API.

### Lab 6: Flask (DB, SQLAlchemy, Alembic)
This lab explores building web applications with Flask, focusing on database integration using SQLAlchemy and Alembic for migrations. The lab covers:
* Flask server deployment and routing.
* Developing views with Jinja templates and WTForms.
* Working with forms and data validation.
* Connecting to databases and working with models.
* Implementing CRUD operations based on user roles.
* Establishing "one-to-many," "one-to-one," and "many-to-many" relationships.
* Applying data migrations manually and automatically with Alembic.

### Lab 7: Flask (User Authorization, Packages)
This lab extends the Flask project from Lab 6 by implementing user authentication, an administrator panel, and structured project organization. Specific tasks include:
* Adding user authentication.
* Implementing an administrator panel with full data and user account access.
* Organizing the project structure using classes, Blueprints, and Flask Application Factory patterns.
