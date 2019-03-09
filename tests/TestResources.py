# Copyright (c) 2017 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.

import os
import platform
from unittest import TestCase
import tempfile
import pytest

from UM.Resources import Resources, ResourceTypeError, UnsupportedStorageTypeError


class TestResources(TestCase):

    #
    # getConfigStorageRootPath() tests
    #
    def test_getConfigStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.getenv("APPDATA")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    def test_getConfigStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        # no XDG_CONFIG_HOME defined
        if "XDG_CONFIG_HOME" in os.environ:
            del os.environ["XDG_CONFIG_HOME"]
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/.config")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

        # XDG_CONFIG_HOME defined
        os.environ["XDG_CONFIG_HOME"] = "/tmp"
        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = "/tmp"
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    def test_getConfigStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        config_root_path = Resources._getConfigStorageRootPath()
        expected_config_root_path = os.path.expanduser("~/Library/Application Support")
        self.assertEqual(expected_config_root_path, config_root_path,
                         "expected %s, got %s" % (expected_config_root_path, config_root_path))

    #
    # getDataStorageRootPath() tests
    #
    def test_getDataStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    def test_getDataStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        # no XDG_CONFIG_HOME defined
        if "XDG_DATA_HOME" in os.environ:
            del os.environ["XDG_DATA_HOME"]
        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = os.path.expanduser("~/.local/share")
        self.assertEqual(expected_data_root_path, data_root_path,
                         "expected %s, got %s" % (expected_data_root_path, data_root_path))

        # XDG_CONFIG_HOME defined
        os.environ["XDG_DATA_HOME"] = "/tmp"
        data_root_path = Resources._getDataStorageRootPath()
        expected_data_root_path = "/tmp"
        self.assertEqual(expected_data_root_path, data_root_path,
                         "expected %s, got %s" % (expected_data_root_path, data_root_path))

    def test_getDataStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        data_root_path = Resources._getDataStorageRootPath()
        self.assertIsNone(data_root_path, "expected None, got %s" % data_root_path)

    #
    # getCacheStorageRootPath() tests
    #
    def test_getCacheStorageRootPath_Windows(self):
        if platform.system() != "Windows":
            self.skipTest("not on Windows")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.getenv("LOCALAPPDATA")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    def test_getCacheStorageRootPath_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        cache_root_path = Resources._getCacheStorageRootPath()
        expected_cache_root_path = os.path.expanduser("~/.cache")
        self.assertEqual(expected_cache_root_path, cache_root_path,
                         "expected %s, got %s" % (expected_cache_root_path, cache_root_path))

    def test_getCacheStorageRootPath_Mac(self):
        if platform.system() != "Darwin":
            self.skipTest("not on mac")

        cache_root_path = Resources._getCacheStorageRootPath()
        self.assertIsNone("expected None, got %s" % cache_root_path)

    def test_getPossibleConfigStorageRootPathList_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        # We didn't add any paths, so it will use defaults
        assert Resources._getPossibleConfigStorageRootPathList() == ['/tmp/test']

    def test_getPossibleDataStorageRootPathList_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")
        # We didn't add any paths, so it will use defaults
        assert Resources._getPossibleDataStorageRootPathList() == ['/tmp/test']

    def test_factoryReset(self):
        Resources.factoryReset()
        # Check if the data is deleted!
        assert len(os.listdir(Resources.getDataStoragePath())) == 0

        # The data folder should still be there, but it should also have created a zip with the data it deleted.
        assert len(os.listdir(os.path.dirname(Resources.getDataStoragePath()))) == 2

        # Clean up after our ass.
        folder = os.path.dirname(Resources.getDataStoragePath())
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            print(file_path)
            try:
                os.unlink(file_path)
            except:
                pass
        folder =  os.path.dirname(Resources.getDataStoragePath())
        for file in os.listdir(folder):
            file_path = os.path.join(folder, file)
            try:
                os.unlink(file_path)
            except:
                pass

    def test_copyLatestDirsIfPresent(self):
        # Just don't fail.
        Resources._copyLatestDirsIfPresent()

    def test_getStoragePathForType_Linux(self):
        if platform.system() != "Linux":
            self.skipTest("not on Linux")

        with pytest.raises(ResourceTypeError):
            # No types have been added, so this should break!
            Resources.getAllResourcesOfType(0)
        with pytest.raises(UnsupportedStorageTypeError):
            # We still haven't added it, so it should fail (again)
            Resources.getStoragePathForType(0)

        Resources.addStorageType(0, "/test")
        assert Resources.getStoragePathForType(0) == "/test"

    def test_getAllResourcesOfType(self):
        resouce_folder = tempfile.mkdtemp("test_folder_origin")
        resource_file = tempfile.mkstemp(dir=str(resouce_folder))
        Resources.addStorageType(111, resouce_folder)
        assert Resources.getAllResourcesOfType(111) == [resource_file[1]]

    def test_copyVersionFolder(self):

        import os
        folder_to_copy = tempfile.mkdtemp("test_folder_origin")
        file_to_copy = tempfile.mkstemp(dir=str(folder_to_copy))

        folder_to_move_to = tempfile.mkdtemp("test_folder_destination")

        Resources.copyVersionFolder(str(folder_to_copy), str(folder_to_move_to) + "/target")
        # We put a temp file in the folder to copy, check if it arrived there.
        assert len(os.listdir(str(folder_to_move_to) + "/target")) == 1

    def test_findLatestDirInPaths(self):
        test_folder = tempfile.mkdtemp("test_folder")
        os.mkdir(os.path.join(test_folder, "whatever"))

        # There is no folder that matches what we're looking for!
        assert Resources._findLatestDirInPaths([test_folder]) is None

        os.mkdir(os.path.join(test_folder, Resources.ApplicationVersion))
        # We should obviously find the folder that was created by means of the ApplicationVersion.
        assert Resources._findLatestDirInPaths([test_folder]) == os.path.join(test_folder, Resources.ApplicationVersion)

    def test_addRemoveStorageType(self):
        Resources.addStorageType(9901, "YAY")
        Resources.addType(9902, "whoo")
        Resources.addStorageType(100, "herpderp")

        with pytest.raises(ResourceTypeError):
            # We can't add the same type again
            Resources.addStorageType(9901, "nghha")

        Resources.removeType(9001)
        Resources.removeType(9902)

        with pytest.raises(ResourceTypeError):
            # We can't do that, since it's in the range of user types.
            Resources.removeType(100)

        with pytest.raises(ResourceTypeError):
            # We can't do that, since it's in the range of user types.
            Resources.addType(102, "whoo")

