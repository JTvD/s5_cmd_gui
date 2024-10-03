"""A class analogous to the pathlib.Path for accessing Scality data."""
from __future__ import annotations
from pathlib import PurePosixPath


class ScalityPath:
    """A class analogous to the pathlib.Path for accessing Scality data.
    """
    def __init__(self, data_operations, *args, Ff=None):
        """Initialize Scality Path object similar to the Path object.

        Args:
            data_operations: instance of the DataOperations class
            Specification of the path. For example: "x/z" or "x", "z".
        """
        self.data_operations = data_operations
        self.Ff = Ff
        args = [a._path if isinstance(a, ScalityPath) else a for a in args]
        self._path = PurePosixPath(*args)
        super().__init__()

    @classmethod
    def from_tree_item(cls, data_operations, tree_item) -> ScalityPath:
        """Initialize ScalityPath from tree item:
            Args:
                data_operations: instance of the DataOperations class
                tree_item: list:
                    [display_name, level, 'F/f', absolute Path]
        """
        return cls(data_operations, tree_item[3], Ff=tree_item[2])

    def absolute(self) -> ScalityPath:
        """Return an absolute version of this path.
        """
        return self

    def __str__(self) -> str:
        """Get the absolute path if converting to string."""
        return str(self.absolute()._path)

    def __repr__(self) -> str:
        """Representation of the ScalityPath object in line with a Path object."""
        return f"ScalityPath({', '.join(self._path.parts)})"

    def __truediv__(self, other) -> ScalityPath:
        """Ensure that we can append just like the Path object."""
        return self.__class__(self._path, other)

    def __getattribute__(self, attr):
        """Make the ScalityPath transparent so that some Path functionality is available."""
        if attr in ["parts"]:
            return self._path.__getattribute__(attr)
        return super().__getattribute__(attr)

    def joinpath(self, *args) -> ScalityPath:
        """Concatenate another path to this one.

        Return:
            The concatenated path.

        """
        return ScalityPath(self.data_operations, self._path, *args)

    @property
    def parent(self) -> ScalityPath:
        """Return:
                the parent directory of the current directory.
        """
        return ScalityPath(self.data_operations, self.absolute()._path.parent)

    @property
    def name(self) -> str:
        """Return:
                the name of the file or folder.
        """
        return self.absolute().parts[-1]

    @property
    def suffix(self):
        """Return the file extension of the path."""
        return self._path.suffix

    def full_path(self) -> str:
        """Return:
                the path with the bucketname to the file or folder
        """
        full_path = ScalityPath(self.data_operations, self.data_operations.bucket_name).joinpath(self.absolute())._path
        # File
        if full_path.suffix:
            return "s3://" + str(full_path)
        # Folders get a trailing /
        return "s3://" + str(full_path) + '/'

    def relative_path(self) -> str:
        """Return:
                the path to the file or folder without bucketname
        """
        full_path = self.absolute()._path
        # File
        if full_path.suffix:
            return str(full_path)
        # Folders get a trailing /
        return str(full_path) + '/'

    def remove(self):
        """Remove the file or folder."""
        if self.data_operations.check_scality_path_exists(self.absolute()):
            self.data_operations.delete_bucket_data(self.absolute())

    def exists(self) -> bool:
        """Check if the path is a directory."""
        return self.data_operations.check_scality_path_exists(self.absolute())


if __name__ == "__main__":
    from data_operation import DataOperation
    do = DataOperation()
    sc = ScalityPath(do, 'test.txt')
    scb = ScalityPath.from_tree_item(do, ['', 1, 'F', 'test.txt'])
    print(sc.full_path())
    print(scb.full_path())
