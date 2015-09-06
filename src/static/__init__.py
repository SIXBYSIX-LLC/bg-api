"""
******
Static
******
The aim of this app is to handle static files upload for any object (like product images,
user credit form, etc...) and store them to cloud.

We currently use `Cloudinary` for image/file storage

So any other app that needs file storage should make relation(either foreign key or many to many)
with ``static.File`` model

.. todo:: Delete file from upstream server when the delete is called
"""
