"""Azure Blob wrapper package
"""
from flask import _app_ctx_stack
from azure.storage.blob import BlobServiceClient, generate_blob_sas


class FlaskAzure:
    """Class to ease the use of azure blob storage functions.
    provides clean interface to upload, download and delete blob files from path.
    """

    def __init__(self, app=None):
        self.app = app
        if app is not None:
            self.init_app(app)

    def init_app(self, app, **kwargs):
        """Intialize azure blob

        Args:
            app (flask app)
        """
        app.config.setdefault("AZURE_STORAGE_CONNECTION_STRING", None)
        app.config.setdefault("AZURE_STORAGE_CONTAINER_NAME", None)

        app.teardown_appcontext(self.teardown)

    def teardown(self, exception):
        """Close azure blob connection"""
        ctx = _app_ctx_stack.top
        if hasattr(ctx, "azure_blob_connector"):
            ctx.azure_blob_connector.close()

    @property
    def blob_connector(self):
        """Get blob storage connection
            Used to connect to the storage account using connection string
        Returns:
            [BlobServiceClient]: A blob service client
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            if not hasattr(ctx, "azure_blob_connector"):
                ctx.azure_blob_connector = BlobServiceClient.from_connection_string(
                    ctx.app.config.get("AZURE_STORAGE_CONNECTION_STRING")
                )
            return ctx.azure_blob_connector
        return None

    def blob_client(self, path: str, container_name=None):
        """Get blob client
            Used to get a specific blob
        Args:
            path (str): directory path in the container

        Returns:
            [BlobClient]: A blob client
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            container_name = container_name or ctx.app.config.get(
                "AZURE_STORAGE_CONTAINER_NAME"
            )
            return self.blob_connector.get_blob_client(
                container=container_name, blob=path,
            )
        return None

    def download(self, path: str, container_name=None, **kwargs):
        """Download the blob from specified path

        Args:
            path (str): path to the blob
            container_name (str,optional): name of the storage container
        Returns:
            [StorageStreamDownloader]: downloaded data
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            return self.blob_client(path, container_name=container_name).download_blob(
                **kwargs
            )
        return None

    def upload(self, path: str, data: bytes, container_name=None, **kwargs):
        """Upload the data in blob storage to specified path

        Args:
            path (str): path to upload the blob
            data (bytes): data to be uploaded
            container_name (str, optional): name of storage container. Defaults to None.

        Returns:
            dict: status of uploaded file
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            return self.blob_client(path, container_name=container_name).upload_blob(
                data, overwrite=True, **kwargs
            )
        return None

    def delete(self, path: str, container_name=None, **kwargs):
        """Delete blob in blob storage from the specified path

        Args:
        Returns:
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            return self.blob_client(path, container_name=container_name).delete_blob(
                **kwargs
            )
        return None

    def list_blobs(self, folder_path: str, **kwargs) -> list:
        """List the file names in the container

        Args:
            folder_path (str): absolute path of folder

        Returns:
            list: List of filenames at the given folder path.
        """

        ctx = _app_ctx_stack.top
        if ctx is not None:
            files = self.blob_connector.get_container_client(
                ctx.app.config.get("AZURE_STORAGE_CONTAINER_NAME")
            ).list_blobs(name_starts_with=folder_path)

            return [file.name.split("/")[-1] for file in files]
        return []

    def url(self, path: str, container_name=None, **kwargs):
        """Get url of blob specified by the `path`

        Args:
            path (str): path to the blob
            container_name (str, optional): Name of the azure container. Defaults to None.

        Returns:
            str: url to the blob, else None
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            return self.blob_client(path, container_name=container_name).url
        return None

    def copy(self, source_url: str, dest_path: str, container_name=None, **kwargs):
        """[summary]

        Args:
            source_url (str): url of blob to be copied
            dest_path (str): destination blob path to copy blob
            container_name (str, optional): Name of the blob container. Defaults to None.

        Returns:
            [type]: [description]
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            return self.blob_client(
                dest_path, container_name=container_name
            ).start_copy_from_url(source_url=source_url)
        return None

    def move(self, source_path: str, dest_path: str, container_name=None, **kwargs):
        """Moves the blob at `source_path` to `dest_path`

        User the source blobs `url` to copy.

        Args:
            source_path (str): source path of blob
            dest_path (str): destination path of the blob
            container_name (str, optional): Name of azure container. Defaults to None.

        Returns:
            bool: True if moved succesfully, else None
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            source_blob_url = self.url(source_path, container_name=container_name)
            print(source_blob_url, dest_path)
            self.copy(
                source_blob_url, dest_path=dest_path, container_name=container_name
            )

            self.delete(path=source_path, container_name=container_name)
            return True
        return None

    def get_sas_token_for_blob(self, file_path, container_name=None, **kwargs):
        ctx = _app_ctx_stack.top
        if ctx is not None:
            container_name = container_name or ctx.app.config.get(
                "AZURE_STORAGE_CONTAINER_NAME"
            )
            return generate_blob_sas(
                account_name=self.blob_connector.account_name,
                container_name=container_name,
                account_key=self.blob_connector.credential.account_key,
                blob_name=file_path,
                expiry=kwargs.get("expiry"),
                start=kwargs.get("start"),
                permission=kwargs.get("permission"),
            )
        return None

    def get_blob_access_with_sas(self, file_path, container_name=None, **kwargs):
        """Get the url with SAS token for a blob with only `Read` access.

        Args:
            file_path (str): path to blob file
            container_name (str, optional): Name of blob container. Defaults to None.

        Returns:
            str: url with sas token for the blob
        """
        ctx = _app_ctx_stack.top
        if ctx is not None:
            url = self.url(file_path, container_name)
            sas = self.get_sas_token_for_blob(file_path, **kwargs)
            return "{0}?{1}".format(url, sas)
        return None
