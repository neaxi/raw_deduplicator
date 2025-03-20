"""tests"""

import unittest
from unittest.mock import patch
from pathlib import Path
import src.main as main


class TestFramework(unittest.TestCase):
    """to verify the unittest framework works correctly"""

    def test_myself(self):
        """test the unittest framework is operational"""
        with self.assertRaises(ValueError):
            raise ValueError("test fail")


class TestMainApplication(unittest.TestCase):
    """test the expected behavior of the application"""

    def setUp(self):
        """Set up temp"""
        self.test_dir = Path("/tmp/test_dir")
        self.orf_dir = self.test_dir / "orf"

    @patch("builtins.input")
    @patch("pathlib.Path.exists")
    def test_pick_folder_valid_paths(self, mock_exists, mock_input):
        """both paths exists"""
        mock_input.return_value = str(self.test_dir)
        mock_exists.side_effect = [True, True]

        src, target = main.pick_folder()
        self.assertEqual(src, self.test_dir)
        self.assertEqual(target, self.orf_dir)

    @patch("builtins.input")
    @patch("pathlib.Path.exists")
    def test_pick_folder_invalid_source(self, mock_exists, mock_input):
        """first folder selection was invalid
        no checks for subfolder are made"""
        mock_input.side_effect = ["invalid", str(self.test_dir)]
        mock_exists.side_effect = [False, True, True]

        src, target = main.pick_folder()
        self.assertEqual(src, self.test_dir)
        self.assertEqual(target, self.orf_dir)

    @patch("builtins.input")
    @patch("pathlib.Path.exists")
    def test_pick_folder_missing_orf(self, mock_exists, mock_input):
        """first folder selection is valid, but there is no matching subfolder"""
        mock_input.side_effect = [str(self.test_dir), str(self.test_dir)]
        mock_exists.side_effect = [True, False, True, True]

        src, target = main.pick_folder()
        self.assertEqual(src, self.test_dir)
        self.assertEqual(target, self.orf_dir)

    @patch("pathlib.Path.iterdir")
    def test_identify_files_empty_folders(self, mock_iterdir):
        """both folders are empty"""
        mock_iterdir.return_value = []
        files = main.identify_files_for_removal(self.test_dir, self.orf_dir)
        self.assertEqual(files, [])

    @patch("pathlib.Path.iterdir")
    def test_identify_files_with_matches(self, mock_iterdir):
        """only file test3 should get picked for deletion"""
        jpg_files = [Path("test1.jpg"), Path("test2.JPG")]
        orf_files = [
            Path("test1.orf"),
            Path("test2.orf"),
            Path("test2-1.orf"),
            Path("test3.orf"),
        ]
        mock_iterdir.side_effect = [jpg_files, orf_files]

        files = main.identify_files_for_removal(self.test_dir, self.orf_dir)
        self.assertEqual(len(files), 1)
        self.assertEqual(files[0].name, "test3.orf")

    def test_pprint_files_from_different_folders(self):
        """raise AttributeError due to different folders"""
        files = [Path("/tmp/dir1/test.orf"), Path("/tmp/dir2/test.orf")]
        with self.assertRaises(AttributeError):
            main.pprint_list_of_files(files)

    @patch("builtins.print")
    def test_pprint_files_formatting(self, mock_print):
        files = [Path("/tmp/test_dir/test1.orf"), Path("/tmp/test_dir/test2.orf")]
        main.pprint_list_of_files(files)
        mock_print.assert_called()

    @patch("builtins.input")
    def test_confirm_prompt_valid_responses(self, mock_input):
        valid_responses = ["y", "Y", "yes", "Yes", "YES"]
        for response in valid_responses:
            mock_input.return_value = response
            self.assertTrue(main.confirm_prompt())

    @patch("builtins.input")
    def test_confirm_prompt_invalid_responses(self, mock_input):
        invalid_responses = ["n", "no", "NO", "", "maybe"]
        for response in invalid_responses:
            mock_input.return_value = response
            self.assertFalse(main.confirm_prompt())

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.unlink")
    def test_delete_files(self, mock_unlink, mock_is_file):
        mock_is_file.return_value = True
        files = [Path("/tmp/test.orf"), Path("/tmp/test2.orf")]
        main.delete_files(files)
        self.assertEqual(mock_unlink.call_count, 2)

    @patch("pathlib.Path.is_file")
    @patch("pathlib.Path.unlink")
    def test_delete_files_some_missing(self, mock_unlink, mock_is_file):
        mock_is_file.side_effect = [True, False]
        files = [Path("/tmp/test.orf"), Path("/tmp/missing.orf")]
        main.delete_files(files)
        self.assertEqual(mock_unlink.call_count, 1)

    @patch("src.main.pick_folder")
    @patch("src.main.identify_files_for_removal")
    @patch("src.main.confirm_prompt")
    @patch("src.main.delete_files")
    def test_main_no_files_found(
        self, mock_delete, mock_confirm, mock_identify, mock_pick
    ):
        """no files found -> SystemExit + delete not called"""
        mock_pick.return_value = (self.test_dir, self.orf_dir)
        mock_identify.return_value = []

        with self.assertRaises(SystemExit):
            main.main()

        mock_delete.assert_not_called()
        mock_confirm.assert_not_called()

    @patch("src.main.pick_folder")
    @patch("src.main.identify_files_for_removal")
    @patch("src.main.confirm_prompt")
    @patch("src.main.delete_files")
    def test_main_user_aborts(
        self, mock_delete, mock_confirm, mock_identify, mock_pick
    ):
        """deletion confirmation was False -> delete not called"""
        mock_pick.return_value = (self.test_dir, self.orf_dir)
        mock_identify.return_value = [Path("test.orf")]
        mock_confirm.return_value = False

        main.main()

        mock_delete.assert_not_called()
