# mongodb_utils.py

import pymongo
import logging
from dimple_utils import config_utils

# Global variables. These are initialized in the initialize() function. Any module using this module should
# use these variables after setting as global variables in their module.

mongodb_client = None

def initialize():
    global mongodb_client
    """
    Returns a MongoDB client connected to the specified URI.

    :param uri: MongoDB connection URI.
    :return: A pymongo MongoClient instance.
    """
    host = config_utils.get_property('mongodb.host', fallback='localhost')
    port = config_utils.get_int_property('mongodb.port', fallback=27017)
    username = config_utils.get_property('mongodb.username', fallback=None)
    password = config_utils.get_secret('mongodb.password')
    auth_source = config_utils.get_property('mongodb.auth_source', fallback='admin')
    ssl_enabled = config_utils.get_bool_property('mongodb.ssl_enabled', fallback=False)

    logging.info(f"host={host}, port={port}, username={username}, auth_source={auth_source}, ssl_enabled={ssl_enabled}")

    try:
        # Build the MongoDB URI
        if username and password:
            mongo_uri = f"mongodb://{username}:{password}@{host}:{port}/?authSource={auth_source}"
        else:
            mongo_uri = f"mongodb://{host}:{port}/"

        # Additional connection options
        options = {}
        if ssl_enabled:
            options['ssl'] = True
            # Optionally, add SSL certificates if needed
            # options['ssl_cert_reqs'] = 'CERT_REQUIRED'
            # options['ssl_ca_certs'] = '/path/to/ca_certificate.pem'

        mongodb_client = pymongo.MongoClient(mongo_uri, **options)
        logging.info("Connected to MongoDB...")
        return mongodb_client
    except Exception as e:
        logging.error(f"Failed to connect to MongoDB: {e}. uri={uri}")
        raise

def get_mongodb_database(db_name):
    global mongodb_client
    return mongodb_client[db_name]

def collection_exists(db_name, collection_name):
    db = get_mongodb_database(db_name=db_name)
    return collection_name in db.list_collection_names()

def get_mongodb_collection(collection_name, db=None, db_name=None ):
    global mongodb_client
    if not db:
        if not db_name:
            raise Exception(f"Both db and db_name is null. One of it needs to be provided to "
                            f"create the collection {collection_name}")
        db = get_mongodb_database(db_name)
    return db[collection_name]

def create_collection(db_name, collection_name, validator=None):
    global mongodb_client
    db = get_mongodb_database(db_name=db_name)
    try:
        db.create_collection(collection_name, validator=validator)
        logging.info(f"Collection {db_name}:{collection_name} created")
    except Exception as e:
        if "already exists" in f"{e}":
            logging.info(f"Collection {db_name}:{collection_name} already existing. Ignoring")
        else:
            raise

def create_index(db_name, collection_name, field_name, unique=False):
    global mongodb_client
    collection = get_mongodb_collection(collection_name, db_name=db_name)
    try:
        collection.create_index([(field_name, 1)], unique=unique)
        logging.info(f"Created index on {field_name} for collection {collection_name}.")
    except Exception as e:
        logging.error(f"Failed to create index on {field_name} for collection {collection_name}: {e}")
        raise

def update_collection_validator(db_name, collection_name, validator):
    db = get_mongodb_database(db_name=db_name)
    try:
        db.command({
            "collMod": collection_name,
            "validator": validator,
            "validationLevel": "moderate"  # You can adjust the validation level as needed
        })
        logging.info(f"Validator for collection {db_name}:{collection_name} updated successfully")
    except Exception as e:
        logging.error(f"Failed to update validator for collection {db_name}:{collection_name}: {str(e)}")
        raise


def find_documents(db_name, collection_name, query, sort=None):
    db = get_mongodb_database(db_name=db_name)
    try:
        if sort:
            documents = list(db[collection_name].find(query).sort(sort))
        else:
            documents = list(db[collection_name].find(query))
        logging.info(f"Documents retrieved successfully from {db_name}:{collection_name}")
        return documents
    except Exception as e:
        logging.error(f"Failed to retrieve documents from {db_name}:{collection_name}: {str(e)}")
        return None


def find_one(db_name, collection_name, filter_query, sort=None):
    global mongodb_client
    """
    Finds a single document in the specified MongoDB collection.

    :param db_name: The MongoDB database name.
    :param collection_name: Name of the collection to find the document in.
    :param filter_query: A dictionary specifying the filter for the document to find.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        document = collection.find_one(filter_query) if sort is None else collection.find(filter_query).sort(sort).limit(1).next()
        logging.debug(f"Found document in MongoDB collection '{collection_name}' with filter '{filter_query}'.")
        return document
    except Exception as e:
        logging.error(f"Failed to find document in MongoDB: {e}")
        raise

def insert_one(db_name, collection_name, document):
    global mongodb_client
    """
    Inserts a single document into the specified MongoDB collection.

    :param db: The MongoDB database object.
    :param collection_name: Name of the collection to insert data into.
    :param document: A dictionary containing the document to insert.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        result = collection.insert_one(document)
        logging.debug(f"Inserted document with ID '{result.inserted_id}' into MongoDB collection '{collection_name}'.")
    except Exception as e:
        logging.error(f"Failed to insert document into MongoDB: {e}")
        raise

def insert_many(db_name, collection_name, documents):
    global mongodb_client
    """
    Inserts the scan results into the specified MongoDB collection.

    :param db: The MongoDB database object.
    :param collection_name: Name of the collection to insert data into.
    :param rows: A list of dictionaries containing rows to insert.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        result = collection.insert_many(documents)
        logging.debug(f"Inserted {len(result.inserted_ids)} documents into MongoDB collection '{collection_name}'.")
    except Exception as e:
        logging.error(f"Failed to insert documents into MongoDB: {e}")
        raise

def update_one(db_name, collection_name, filter_query, update_data):
    global mongodb_client
    """
    Updates a single document in the specified MongoDB collection.

    :param db_name: The MongoDB database name.
    :param collection_name: Name of the collection to update data in.
    :param filter_query: A dictionary specifying the filter for the document to update.
    :param update_data: A dictionary specifying the fields to update.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        result = collection.update_one(filter_query, update_data)
        logging.debug(f"Updated document in MongoDB collection '{collection_name}' with filter '{filter_query}'.")
        return result
    except Exception as e:
        logging.error(f"Failed to update document in MongoDB: {e}")
        raise

def update_many(db_name, collection_name, filter_query, update_values):
    """
    Updates multiple documents in the specified MongoDB collection.

    :param db_name: The MongoDB database name.
    :param collection_name: Name of the collection to update.
    :param filter_query: A dictionary specifying the filter for documents to update.
    :param update_values: A dictionary specifying the update operations to be applied.
    :return: The result of the update operation.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        result = collection.update_many(filter_query, update_values)
        logging.info(f"Updated {result.modified_count} documents in '{collection_name}' collection.")
        return result
    except Exception as e:
        logging.error(f"Failed to update documents in '{collection_name}' collection: {e}")
        raise

def delete_one(db_name, collection_name, filter_query):
    global mongodb_client
    """
    Deletes a single document from the specified MongoDB collection.

    :param db_name: The MongoDB database name.
    :param collection_name: Name of the collection to delete data from.
    :param filter_query: A dictionary specifying the filter for the document to delete.
    """
    try:
        db = mongodb_client[db_name]
        collection = db[collection_name]
        result = collection.delete_one(filter_query)
        logging.debug(f"Deleted document from MongoDB collection '{collection_name}' with filter '{filter_query}'.")
        return result
    except Exception as e:
        logging.error(f"Failed to delete document from MongoDB: {e}")
        raise

def close_mongo_client():
    global mongodb_client
    """
    Closes the MongoDB client connection.

    :param client: The MongoClient instance to close.
    """
    try:
        if mongodb_client:
            mongodb_client.close()
        logging.info("Closed MongoDB connection.")
    except Exception as e:
        logging.error(f"Failed to close MongoDB connection: {e}", exc_info=True)
