from webapp_shell.native.start_location import StartLocation


def test_a_folder_opens_itself(tmp_path):
    assert StartLocation.of(str(tmp_path)) == StartLocation(str(tmp_path))


def test_a_file_opens_its_folder_with_the_name_preselected(tmp_path):
    file = tmp_path / "people.xlsx"
    file.write_text("x")
    location = StartLocation.of(str(file))
    assert (location.directory, location.filename) == (str(tmp_path), "people.xlsx")
    assert location.qt_path() == str(file)


def test_a_missing_path_falls_back_to_the_nearest_existing_folder(tmp_path):
    assert StartLocation.of(str(tmp_path / "gone" / "deeper")).directory == str(tmp_path)
    assert StartLocation.of(str(tmp_path / "new.pdf")) == StartLocation(str(tmp_path), "new.pdf")


def test_nothing_chosen_leaves_it_to_the_toolkit():
    assert StartLocation.of("") == StartLocation.of(None) == StartLocation()
    assert StartLocation().qt_path() == ""
