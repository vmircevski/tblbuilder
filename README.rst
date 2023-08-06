=====================================================
TblApp - Dynamic Table CRUD for Django Rest Framework
=====================================================

Simple backend for a table builder app, where the user can build tables dynamically. The app has the following endpoints:

.. list-table:: TblApp API
   :widths: 25 25 50
   :header-rows: 1

   * - Request Type
     - Endpoint
     - Action
   * - POST
     - /api/table
     - Generates dynamic Django model based on user provided fields types and names. The field type can be a string, number or boolean.
   * - PUT
     - /api/table/:id
     - Allows the user to update the structure of dynamically generated model.
   * - POST
     - /api/table/:id/row
     - Allows the user to add rows to the dynamically generated model while respecting the model schema
   * - GET
     - /api/table/:id/rows
     - Gets all the rows in the dynamically generated model


* Free software: MIT license
* Documentation: this file

Features
--------

* it is based on Django REST framework
* uses PostgreSQL as DB backend
* exceptions for possible cases are handled via custom exception class
* black is used for formatting
* altering columns supports column name and column type change
* dynamic table metadata is saved in "dyntbl" table
* Django model is created in runtime from "dyntbl" table
* Dynamic Table Serializer is created in runtime from the dynamic model

Install
-------

Database setup
==============

Make sure that PostgreSQL database: 'tblapp' is present.
In settings.py db user/pass is: tblapp / tblapp and the DB is also: tblapp
Steps for creating user and PostgreSQL database on Debian linux would be:

.. code-block:: shell

                su -
                su - postgres -c psql
                postgres=# create database tblapp;
                postgres=# create user tblapp with encrypted password 'tblapp';
                postgres=# grant all privileges on database tblapp to tblapp;

Python virtualenv setup
=======================

Virtualenv is not required but is recommended. Python version 3.10.8 was used for developing this library, however newer ones should be compatible also.

In the source directory run these commands.

.. code-block:: shell

                pip install -r requirements_dev.txt
                python manage.py migrate
                python manage.py runserver

Server will run in development mode on http://127.0.0.1:8000

Usage
-----
There is `Insomnia REST client`_ export file **'insomnia_export.json'** in the root of the repo.
Insomnia requests should be run from top to bottom i.e. 'create table', 'add column' etc.

.. _`Insomnia REST client`: https://insomnia.rest/
