from unittest.mock import patch, MagicMock
from src.vectorstore.opensearch_client import OpenSearchVectorStore
import os

@patch("src.vectorstore.opensearch_client.OpenSearch")
def test_index_created(mock_os, monkeypatch):
    monkeypatch.setenv("OPENSEARCH_ENDPOINT","https://host")
    monkeypatch.setenv("OPENSEARCH_INDEX","index")

    mock_client = MagicMock()
    mock_client.indices.exists.return_value = False
    mock_os.return_value = mock_client

    store = OpenSearchVectorStore()
    store.create_if_not_exists(10)

    mock_client.indices.create.assert_called_once()

""" 
    Purpose of This Test

    It verifies that:

    ✔ When the index does NOT exist,
    → your code calls indices.create() exactly once.

    This ensures the ingestion service correctly initializes the OpenSearch index.

    🔍 Line-by-line Explanation
    1. Importing test utilities
    from unittest.mock import patch, MagicMock


    These let you fake OpenSearch so your tests do NOT make real OpenSearch calls.

    2. Importing the class under test
    from src.vectorstore.opensearch_client import OpenSearchVectorStore


    This is the class that your ingestion pipeline uses to index data.

    3. Patching the OpenSearch client
    @patch("src.vectorstore.opensearch_client.OpenSearch")
    def test_index_created(mock_os, monkeypatch):


    This line replaces the real OpenSearch client with a fake (mock) object.

    Why?

    Because in unit tests you should avoid:

    connecting to real OpenSearch

    requiring network

    needing credentials

    polluting real indexes

    So mock_os becomes the fake OpenSearch constructor.

    4. Setting fake environment variables
    monkeypatch.setenv("OPENSEARCH_ENDPOINT","https://host")
    monkeypatch.setenv("OPENSEARCH_INDEX","index")


    Your OpenSearchVectorStore class reads from os.getenv.
    This ensures the test has valid values.

    5. Creating the fake OpenSearch client
    mock_client = MagicMock()
    mock_client.indices.exists.return_value = False
    mock_os.return_value = mock_client


    This simulates:

    Calling OpenSearch() returns mock_client

    Calling mock_client.indices.exists() returns False

    Meaning:

    The index does NOT exist.

    So your code should attempt to create it.

    6. Instantiate your class (under test)
    store = OpenSearchVectorStore()


    Because you patched OpenSearch, the internal line:

    self.client = OpenSearch(...)


    returns your mock_client.

    7. Call the method to test
    store.create_if_not_exists(10)


    This should run:

    indices.exists("index") → False

    So call → indices.create("index", body=...)

    8. Verify the index was created
    mock_client.indices.create.assert_called_once()


    This is the key assertion.

    It ensures that:

    ✔ Index creation was triggered
    ✔ Called exactly once
    ✔ Called with correct logic 

    @patch Does

    @patch temporarily replaces (mocks) a real object with a fake object during a test.

    @patch("src.vectorstore.opensearch_client.OpenSearch")
    def test_index_created(mock_os, monkeypatch):
    This means:

    👉 Replace OpenSearch inside src.vectorstore.opensearch_client
    👉 With a MagicMock object
    👉 Called mock_os
    So inside this test:

    python
    Copy code
    OpenSearch()   →   MagicMock()

"""