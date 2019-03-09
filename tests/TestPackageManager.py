# Copyright (c) 2018 Ultimaker B.V.
# Uranium is released under the terms of the LGPLv3 or higher.
import os
import pytest
import unittest.mock
from unittest.mock import MagicMock, patch

from UM.PackageManager import PackageManager

test_package_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)) + "/UnitTestPackage.package")



@unittest.mock.patch.object(PackageManager, "__init__", lambda *args, **kwargs: None)
def test_comparePackageVersions():
    test_cases = [
        # same versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "1.0"},
         "info_dict2": {"sdk_version": "1",
                        "package_version": "1.0"},
         "expected_result": 0},

        # same package versions, different sdk versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "1.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "1.0"},
         "expected_result": -1},

        # different package versions, same sdk versions
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "1",
                        "package_version": "1.0"},
         "expected_result": 1},

        # different package versions, different sdk versions  #1
        {"info_dict1": {"sdk_version": "1",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "1.0"},
         "expected_result": -1},

        # different package versions, different sdk versions  #2
        {"info_dict1": {"sdk_version": "7",
                        "package_version": "3.0"},
         "info_dict2": {"sdk_version": "3",
                        "package_version": "6.0"},
         "expected_result": -1},
    ]

    package_manager = PackageManager()
    for test_case_dict in test_cases:
        info_dict1 = test_case_dict["info_dict1"]
        info_dict2 = test_case_dict["info_dict2"]
        expected_result = test_case_dict["expected_result"]

        assert expected_result == package_manager._comparePackageVersions(info_dict1, info_dict2)


def test_getLicence():
    manager = PackageManager(MagicMock())
    assert manager.getPackageLicense(test_package_path) == "Do whatever you want with this.\n"


def test_installAndRemovePackage():
    mock_application = MagicMock()
    mock_registry = MagicMock()
    mock_registry.isActivePlugin = MagicMock(return_value = False)
    mock_application.getPluginRegistry = MagicMock(return_value = mock_registry)
    manager = PackageManager(mock_application)
    manager.installedPackagesChanged = MagicMock()
    manager.installPackage(test_package_path)
    assert manager.installedPackagesChanged.emit.call_count == 1
    assert manager.isPackageInstalled("UnitTestPackage")

    info = manager.getInstalledPackageInfo("UnitTestPackage")
    assert info["author"]["author_id"] == "nallath"
    assert info["display_name"] == "UnitTestPackage"

    # We don't want the package to be purged. We need that package for the other tests!
    with patch("os.remove", MagicMock()):
        manager._installPackage({"package_info": info, "filename": test_package_path})

    assert "UnitTestPackage" in manager.getAllInstalledPackageIDs()
    assert manager.isUserInstalledPackage("UnitTestPackage")
    assert manager.getAllInstalledPackagesInfo()["plugin"][0]["display_name"] == "UnitTestPackage"
    manager.initialize()
    # Now to remove the package again!
    manager.removePackage("UnitTestPackage")
    assert manager.installedPackagesChanged.emit.call_count == 2


def test_getPackageInfo():
    manager = PackageManager(MagicMock())
    info = manager.getPackageInfo(test_package_path)

    assert info["author"]["author_id"] == "nallath"
    assert info["display_name"] == "UnitTestPackage"


def test_emptyInit():
    manager = PackageManager(MagicMock())

    assert not manager.getAllInstalledPackageIDs()
    assert not manager.getAllInstalledPackagesInfo()

    manager.installedPackagesChanged = MagicMock()
    manager.removePackage("packageThatDoesNotExist")
    assert manager.installedPackagesChanged.emit.call_count == 0

    assert manager.getBundledPackageInfo("packageThatDoesNotExist") is None

    with pytest.raises(FileNotFoundError):
        assert manager.getPackageLicense("FileThatDoesntExist.package") == {}

    assert manager.getPackageFiles("packageThatDoesNotExist") == []

    assert manager.getPackageContainerIds("packageThatDoesNotExist") == []

