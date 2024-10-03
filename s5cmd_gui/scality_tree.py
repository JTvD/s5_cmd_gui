"""Tree model for Scality collections.
"""
import concurrent.futures
from PySide6.QtGui import QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QFileIconProvider
from boto3 import Session
from os import getenv


class scalityTreeModel(QStandardItemModel):
    """ Model for an scality tree view."""

    def __init__(self, tree_view):
        """ Initialise the tree view with the root node and first level.

        Args:
            tree_view : PySide6.QtWidgets
                Defined Scality tree view UI element.
        """
        super().__init__()
        self.tree_view = tree_view
        session = Session(profile_name=getenv('AWS_PROFILE'))
        self.s3 = session.client('s3', endpoint_url=getenv('ENDPOINT'))
        # Empty tree
        self.clear()

    def _tree_row_from_item(self, item: str, prefix: str, level: int, file_folder: str='f'):
        """ Item is the full path to the file/folder:
            - test/1/1-20240319-103924-001/20240319-AmbientLightSensor.txt
            - test/1/1-20240319-103924-001/INS

            Args:
                item : str
                    Full path to the file or folder
                prefix : str
                    Prefix of the path
                level : int
                    Level in the tree
                file_folder : str
                    'F' for folder, 'f' for file
        """
        if item == '.':
            item = ''
        icon_provider = QFileIconProvider()
        display = QStandardItem(item.removeprefix(prefix).rstrip('/'))
        if file_folder == 'f':
            display.setIcon(icon_provider.icon(QFileIconProvider.IconType.File))
        else:
            display.setIcon(icon_provider.icon(QFileIconProvider.IconType.Folder))
        row = [
            display,  # display name
            QStandardItem(str(level + 1)),  # item level in the tree
            QStandardItem(file_folder),  # F (Folder) or f (file)
            QStandardItem(item),  # full path to the file or folder
        ]
        return row

    def init_tree(self):
        """ Draw the first levels of an Scality filesystem as a tree.
        """
        self.setRowCount(0)
        root = self.invisibleRootItem()

        root_row = self._tree_row_from_item(".", "", 1, 'F')
        root.appendRow(root_row)
        new_node = root.child(root.rowCount() - 1)

        # Check if there is something in the bucket
        response = self.s3.list_objects_v2(Bucket=getenv('BUCKETNAME'), Prefix='')
        if response['KeyCount'] > 0:
            # insert a dummy child to get the link to open the collection
            new_node.appendRow(None)

    def delete_subtree(self, tree_item):
        """ Delete subtree.

        Args:
            tree_item : QStandardItem
                Item in the QTreeView
        Return:
            -
        """
        # Remove all children from tree_item
        tree_item.removeRows(0, tree_item.rowCount())

    def add_subtree(self, tree_item, tree_item_data: list):
        """ Grow tree_view from tree_item.

        Args:
            tree_item : PyQt6.QtGui.QStandardItem
                The root of the subtree in the tree view
            tree_item_data : list
                [display_name, level, 'F/f', absolute Path]
        Return:
            -
        """
        _, level, _, abs_path = tree_item_data

        # Assume that tree_item has no children yet.
        paginator = self.s3.get_paginator('list_objects')
        result = paginator.paginate(Bucket=getenv('BUCKETNAME'), Prefix=abs_path, Delimiter='/')
        # Folders
        for prefix in result.search('CommonPrefixes'):
            if prefix is None:
                break
            else:
                row = self._tree_row_from_item(prefix.get('Prefix'), abs_path, int(level), 'F')
                tree_item.appendRow(row)
                # Insert a dummy child to get the link to open the collection
                tree_item.child(tree_item.rowCount() - 1).appendRow(None)
        # Objects
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = []
            for page in result:
                if page is not None and 'Contents' in page:
                    for obj in page['Contents']:
                        futures.append(executor.submit(self.process_object, obj, abs_path, level, tree_item))
        # Wait for all operations to complete
        concurrent.futures.wait(futures)

    def process_object(self, obj, abs_path, level, tree_item):
        row = self._tree_row_from_item(obj['Key'], abs_path, int(level))
        tree_item.appendRow(row)

    def refresh_subtree(self, position):
        """ Refresh the tree view.

        Args:
            position : PyQt6.QtCore.QModelIndex
                Location in tree
        Return:
            -
        """
        model_index = position
        # clicked item
        tree_item = self.itemFromIndex(model_index)
        parent = tree_item.parent()
        if parent is None:
            parent = self.invisibleRootItem()
        row = tree_item.row()
        # retrieve information of clicked item, the information is stored in its parent
        tree_item_data = [parent.child(row, col).data(0) for col in range(parent.columnCount())]
        # check if folder
        if tree_item_data[2] == 'F':
            # Delete subtree in irodsFsdata and the tree_view.
            self.delete_subtree(tree_item)
            self.add_subtree(tree_item, tree_item_data)

    def path_from_tree_index(self, model_index):
        """ Returns the absolute path to the tree index

        Args:
            model_index : PyQt6.QtCore.QModelIndex
                Selected row in tree view
        Return:
            tree_item_data : list
                [display_name, level, 'F/f', absolute Path]
        """
        # clicked item
        tree_item = self.itemFromIndex(model_index)
        row = tree_item.row()

        parent = tree_item.parent()  # contains the data of tree_item
        if parent is None:
            parent = self.invisibleRootItem()
        return [parent.child(row, col).data(0) for col in range(parent.columnCount())]
